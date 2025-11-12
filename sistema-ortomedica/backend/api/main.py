# api/main.py
from __future__ import annotations

import os
import datetime as dt
from typing import Any, Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv

import mysql.connector
from mysql.connector import pooling

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, JWTError
from passlib.hash import bcrypt
from datetime import datetime, timezone



# =========================
# CONFIG
# =========================

# Cargar variables de entorno desde backend/.env
BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND_ROOT / '.env'
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Puedes moverlos a variables de entorno si quieres
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "127.0.0.1"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "inventarios"),
    "charset":  "utf8mb4",
    "use_pure": True,
}

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-me")
JWT_ALG = "HS256"
JWT_TTL_MIN = int(os.getenv("JWT_TTL_MIN", "480"))  # 8h


# =========================
# APP & MIDDLEWARE
# =========================

# api/main.py (imports)
import os, datetime as dt, subprocess, threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# CORS básico para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IngestState:
    busy: bool = False
    status: str = "idle"            # "idle" | "running" | "ok" | "error"
    started_at: str | None = None
    last_success_at: str | None = None
    last_error_at: str | None = None
    last_error_msg: str | None = None

ingest_state = IngestState()


# permitimos al cliente local dev (vite) y variaciones
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pool de conexiones
db_pool = pooling.MySQLConnectionPool(
    pool_name="ortomedica_pool",
    pool_size=5,
    **DB_CONFIG,
)


# =========================
# MODELOS
# =========================

class LoginBody(BaseModel):
    email: str
    password: str


class TokenResp(BaseModel):
    access_token: str


class UserOut(BaseModel):
    email: str
    name: str
    role: str


# =========================
# AUTH UTILS
# =========================

def create_access_token(sub: str, name: str, role: str) -> str:
    exp = dt.datetime.utcnow() + dt.timedelta(minutes=JWT_TTL_MIN)
    payload = {"sub": sub, "name": name, "role": role, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def get_conn():
    return db_pool.get_connection()


def fetch_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        # La tabla users en producción no tiene columna 'name'
        cur.execute(
            "SELECT email, role, password_hash FROM users WHERE email=%s LIMIT 1",
            (email,),
        )
        row = cur.fetchone()
        # Normalizar para que las claves esperadas existan
        if row:
            if isinstance(row, dict):
                row.setdefault("name", "")
            else:
                # Si no es dict (por seguridad), envolver
                row = {"email": row[0], "role": row[1], "password_hash": row[2], "name": ""}
        return row
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


# =========================
# ENDPOINTS AUTH
# =========================

@app.post("/auth/login")
def login(body: LoginBody):
    """Login endpoint that returns a JWT token"""
    user = fetch_user_by_email(body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    if not user.get("password_hash") or not bcrypt.verify(body.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )

    token = create_access_token(
        sub=user["email"],
        name=user.get("name", ""),
        role=user.get("role", "user")
    )
    return TokenResp(access_token=token)

@app.post("/ingest/run")
def ingest_run():
    if ingest_state.busy:
        return {"ok": False, "message": "Ingest ya está en ejecución"}

    ingest_state.busy = True
    ingest_state.status = "running"
    # ⬇️ antes: dt.datetime.utcnow().isoformat()
    ingest_state.started_at = datetime.now(timezone.utc).isoformat()

    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    cmd = os.getenv("INGEST_CMD", "python run_scrapers.py")
    threading.Thread(target=_run_ingest_cmd, args=(cmd, backend_dir), daemon=True).start()
    return {"ok": True}


def get_current_user(authorization: Optional[str] = None) -> UserOut:
    """
    Dependencia simple para endpoints protegidos (si en el futuro los usas).
    Espera header: Authorization: Bearer <token>
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return UserOut(email=payload["sub"], name=payload.get("name", ""), role=payload.get("role", ""))


@app.get("/auth/me", response_model=UserOut)
def me(user: UserOut = Depends(get_current_user)):
    return user


# =========================
# INGEST (público el status)
# =========================

class _IngestState:
    def __init__(self):
        self.busy = False
        self.status = "idle"
        self.started_at: str | None = None
        self.last_success_at: str | None = None

ingest_state = _IngestState()

@app.get("/ingest/status")
def ingest_status():
    return {
        "busy": getattr(ingest_state, "busy", False),
        "status": getattr(ingest_state, "status", "idle"),
        "started_at": getattr(ingest_state, "started_at", None),
        "last_success_at": getattr(ingest_state, "last_success_at", None),
        "last_error_at": getattr(ingest_state, "last_error_at", None),
        "last_error_msg": getattr(ingest_state, "last_error_msg", None),
    }

# Parche de compatibilidad si tu ingest_state existente no tenía estos atributos:
for _name, _default in [
    ("last_success_at", None),
    ("last_error_at", None),
    ("last_error_msg", None),
    ("status", "idle"),
    ("started_at", None),
    ("busy", False),
]:
    if not hasattr(ingest_state, _name):
        setattr(ingest_state, _name, _default)

import threading, subprocess
 
@app.post("/ingest/run")
def ingest_run():
    # evita dobles ejecuciones
    if ingest_state.busy:
        return {"ok": False, "message": "Ingest ya está en ejecución"}

    ingest_state.busy = True
    ingest_state.status = "running"
    ingest_state.started_at = datetime.now(timezone.utc).isoformat()

    # Comando para tu scraping real:
    # define tu comando en variable de entorno INGEST_CMD o usa el default
    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    cmd = os.getenv("INGEST_CMD", "python run_scrapers.py")

    def _worker():
        try:
            # Lanza tu scraper desde el directorio backend/
            subprocess.run(cmd, shell=True, check=True, cwd=backend_dir)
            ingest_state.status = "done"
        except Exception as e:
            ingest_state.status = f"error: {e}"
        finally:
            ingest_state.busy = False

    threading.Thread(target=_worker, daemon=True).start()
    return {"ok": True, "started_at": ingest_state.started_at}


def _run_ingest_cmd(cmd: str, cwd: str = None):
    try:
        rc = subprocess.call(cmd, shell=True, cwd=cwd)
        if rc == 0:
            ingest_state.status = "ok"
            ingest_state.last_success_at = datetime.now(timezone.utc).isoformat()
        else:
            ingest_state.status = "error"
    except Exception:
        ingest_state.status = "error"
    finally:
        ingest_state.busy = False

# =========================
# PRODUCTS (público)
# =========================

@app.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Filtro por sku o nombre"),
):
    """
    Devuelve productos paginados agrupando por SKU, con sus ofertas (bodegas) en 'offers'.
    Lee DIRECTO de inventory_current + stores (+ product_assets).
    """
    offset = (page - 1) * page_size

    where = ""
    params: Dict[str, Any] = {}
    if q and q.strip():
        # Dividir la búsqueda en palabras y buscar cada una
        words = [w.strip() for w in q.strip().split() if w.strip()]
        if words:
            conditions = []
            for idx, word in enumerate(words):
                param_name = f"q_like_{idx}"
                conditions.append(f"(i.sku LIKE %({param_name})s OR i.name LIKE %({param_name})s)")
                params[param_name] = f"%{word}%"
            where = "WHERE " + " AND ".join(conditions)

    total_sql = f"""
        SELECT COUNT(*) AS c
        FROM (
            SELECT i.sku
            FROM inventory_current i
            {where}
            GROUP BY i.sku
        ) t
    """

    rows_sql = f"""
        SELECT
            i.sku,
            i.name,
            NULL                AS brand,
            NULL                AS description,
            pa.image_url        AS image_url,
            i.store_id,
            s.name              AS store_name,
            i.costo             AS cost,
            i.precio            AS price,
            i.existencia        AS stock,
            i.last_seen_at      AS updated_at
        FROM inventory_current i
        LEFT JOIN stores s          ON s.id = i.store_id
        LEFT JOIN product_assets pa ON pa.sku = i.sku
        {where}
        ORDER BY i.name
        LIMIT %(limit)s OFFSET %(offset)s
    """

    page_params = dict(params)
    page_params["limit"] = page_size
    page_params["offset"] = offset

    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)

        # total por SKU distinto
        cur.execute(total_sql, params)
        total = int(cur.fetchone()["c"] or 0)

        # filas planas
        cur.execute(rows_sql, page_params)
        flat: List[Dict[str, Any]] = cur.fetchall()

        # agrupar por sku
        products: Dict[str, Dict[str, Any]] = {}
        for r in flat:
            sku = r["sku"]
            if sku not in products:
                products[sku] = {
                    "sku": sku,
                    "name": r["name"],
                    "brand": r["brand"],             # NULL aquí (no lo usa la lista)
                    "description": r["description"], # NULL aquí (no lo usa la lista)
                    "image_url": r.get("image_url"), # opcional
                    "offers": [],
                }
            # transformar tipos
            price = float(r["price"]) if r["price"] is not None else None
            cost = float(r["cost"]) if r["cost"] is not None else None
            stock = int(r["stock"]) if r["stock"] is not None else None

            updated_iso = None
            u = r.get("updated_at")
            if isinstance(u, dt.datetime):
                updated_iso = u.isoformat()
            elif isinstance(u, str):
                updated_iso = u

            products[sku]["offers"].append({
                "store_id": r["store_id"],
                "store_name": r["store_name"],
                "price": price,
                "cost": cost,
                "stock": stock,
                "updated_at": updated_iso,
            })

        items = list(products.values())

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
        }
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()


# =========================
# HEALTHCHECK
# =========================

@app.get("/")
def root():
    return {"ok": True, "service": "Ortomédica API"}
