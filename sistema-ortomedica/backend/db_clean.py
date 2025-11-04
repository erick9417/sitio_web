from db import _con

# Helper para limpiar toda la base antes de correr los scrapers
def clear_all_inventory():
    """
    Limpia TODAS las tablas de inventario (raw y current) antes de una nueva corrida.
    Esto asegura que cada actualización es un estado fresco, sin datos viejos.
    """
    con = _con(); cur = con.cursor()
    # Truncar inventory_raw (histórico ya no necesario)
    cur.execute("TRUNCATE TABLE inventory_raw")
    # Limpiar inventory_current (estado actual)
    cur.execute("DELETE FROM inventory_current")
    con.commit()
    cur.close(); con.close()