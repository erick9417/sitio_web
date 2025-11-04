import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from passlib.context import CryptContext

# Carga el .env desde la carpeta raíz del backend, no desde api/
# Esto evita problemas cuando se ejecuta este script desde api/ y el .env está en ..
BACKEND_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = BACKEND_ROOT / '.env'
# Forzamos a que .env sobreescriba variables del entorno de la consola
load_dotenv(dotenv_path=ENV_PATH, override=True)
PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")

def db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "inventarios"),
    )

email = "epadilla@ortomedicacr.com"
name = "EPN"
role = "admin"
password = "@dmin123"  # cámbiala

try:
    con = db(); cur = con.cursor()
    cur.execute(
        "INSERT INTO users (email,password_hash,name,role) VALUES (%s,%s,%s,%s)",
        (email, PWD.hash(password), name, role),
    )
    con.commit()
    print("Usuario creado:", email)
except mysql.connector.Error as e:
    print("Error de MySQL:", e)
    raise
finally:
    try:
        cur.close()
    except Exception:
        pass
    try:
        con.close()
    except Exception:
        pass
