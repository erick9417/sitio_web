# db.py
import os
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "inventarios"),
    port=int(os.getenv("DB_PORT", "3306")),
)

def _con():
    return mysql.connector.connect(**CFG)

# ---------------------------------------------------------------------
# Bootstrap de tablas
# ---------------------------------------------------------------------
def ensure_tables():
    con = _con(); cur = con.cursor()
    stmts = [
        # Catálogo de tiendas/bodegas
        """
        CREATE TABLE IF NOT EXISTS stores (
          id INT PRIMARY KEY,
          name VARCHAR(200) NOT NULL
        )
        """,
        # Dump crudo de cada corrida (permite auditoría)
        """
        CREATE TABLE IF NOT EXISTS inventory_raw (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          system_code VARCHAR(40) NOT NULL,
          store_id INT NOT NULL,
          system_id VARCHAR(100) NULL,
          sku VARCHAR(100) NULL,
          name VARCHAR(500) NULL,
          existencia INT NULL,
          costo DECIMAL(16,2) NULL,
          precio DECIMAL(16,2) NULL,
          created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          KEY (system_code, store_id),
          KEY (system_id),
          KEY (sku)
        )
        """,
        # Estado actual por (system_code, store_id, system_id)
        """
        CREATE TABLE IF NOT EXISTS inventory_current (
          system_code VARCHAR(40) NOT NULL,
          store_id INT NOT NULL,
          system_id VARCHAR(100) NOT NULL,
          sku VARCHAR(100) NULL,
          name VARCHAR(500) NULL,
          existencia INT NULL,
          costo DECIMAL(16,2) NULL,
          precio DECIMAL(16,2) NULL,
          last_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          PRIMARY KEY (system_code, store_id, system_id),
          KEY (sku),
          KEY (name(100))
        )
        """
    ]
    for s in stmts:
        cur.execute(s)
    con.commit()
    cur.close(); con.close()

# ---------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------
def ensure_store(store_id: int, name: str):
    con = _con(); cur = con.cursor()
    cur.execute("INSERT IGNORE INTO stores (id, name) VALUES (%s, %s)", (store_id, name))
    con.commit()
    cur.close(); con.close()


# ---------------------------------------------------------------------
# Escribe/actualiza datos
# ---------------------------------------------------------------------
def upsert_inventory_raw(row: dict):
    """
    row = {
      system_code, store_id, system_id, sku, name,
      existencia, costo, precio
    }
    """
    con = _con(); cur = con.cursor()
    cur.execute("""
        INSERT INTO inventory_raw
          (system_code, store_id, system_id, sku, name, existencia, costo, precio)
        VALUES
          (%(system_code)s, %(store_id)s, %(system_id)s, %(sku)s, %(name)s,
           %(existencia)s, %(costo)s, %(precio)s)
    """, row)
    con.commit()
    cur.close(); con.close()

def upsert_inventory_current(row: dict):
    """
    row = {
      system_code, store_id, system_id, sku, name,
      existencia, costo, precio, seen_at (opcional)
    }
    """
    seen_at = row.get("seen_at")
    con = _con(); cur = con.cursor()
    cur.execute("""
        INSERT INTO inventory_current
          (system_code, store_id, system_id, sku, name, existencia, costo, precio, last_seen_at)
        VALUES
          (%(system_code)s, %(store_id)s, %(system_id)s, %(sku)s, %(name)s,
           %(existencia)s, %(costo)s, %(precio)s, COALESCE(%(seen_at)s, CURRENT_TIMESTAMP))
        ON DUPLICATE KEY UPDATE
           sku=VALUES(sku),
           name=VALUES(name),
           existencia=VALUES(existencia),
           costo=VALUES(costo),
           precio=VALUES(precio),
           last_seen_at=VALUES(last_seen_at)
    """, row)
    con.commit()
    cur.close(); con.close()

def prune_old_inventory(system_code: str, store_id: int, older_than_minutes: int = 60):
    """
    Para limpiezas después de una corrida: borra los registros que no se vieron
    en la última pasada (marcados por last_seen_at muy viejo).
    """
    cutoff = datetime.utcnow() - timedelta(minutes=older_than_minutes)
    con = _con(); cur = con.cursor()
    cur.execute("""
        DELETE FROM inventory_current
         WHERE system_code=%s AND store_id=%s AND last_seen_at < %s
    """, (system_code, store_id, cutoff))
    con.commit()
    cur.close(); con.close()

def clear_store_inventory(system_code: str, store_id: int):
    """
    Limpia la tabla 'inventory_raw' para esa tienda/sistema antes de reinsertar
    si así lo deseas. (Opcional)
    """
    con = _con(); cur = con.cursor()
    cur.execute("DELETE FROM inventory_raw WHERE system_code=%s AND store_id=%s",
                (system_code, store_id))
    con.commit()
    cur.close(); con.close()

# ---------------------------------------------------------------------
# Capa de compatibilidad que espera core_scraper_xls.py
#   (no cambia tus tablas actuales)
# ---------------------------------------------------------------------
def begin_ingestion_run(system_code: str, store_id: int) -> int:
    """
    El core pide un run_id; nuestro esquema no lo usa.
    Devolvemos 0 como marcador.
    """
    return 0

def insert_inventory_raw(run_id: int, system_code: str, store_id: int,
                         system_id: str, sku: str, name: str,
                         existencia: int, precio: float, costo: float,
                         rownum: int):
    """
    Puente hacia upsert_inventory_raw().
    """
    upsert_inventory_raw(dict(
        system_code=system_code,
        store_id=store_id,
        system_id=system_id or f"row-{rownum}",
        sku=sku,
        name=name,
        existencia=existencia,
        costo=costo,
        precio=precio,
    ))

def ensure_product_and_alias(system_code: str, system_id: str, sku: str, name: str, store_id: int):
    """
    El core devuelve un 'pid' que luego se usa en upsert_stock().
    Aquí usamos una tupla como identificador lógico.
    """
    return (system_id, sku, name)

def upsert_stock(pid, store_id: int, system_code: str, existencia: int, precio: float, costo: float):
    """
    Traduce el 'pid' anterior a la fila para inventory_current.
    """
    system_id, sku, name = pid
    upsert_inventory_current(dict(
        system_code=system_code,
        store_id=store_id,
        system_id=system_id,
        sku=sku,
        name=name,
        existencia=existencia,
        costo=costo,
        precio=precio,
        seen_at=None  # usa CURRENT_TIMESTAMP por defecto
    ))
