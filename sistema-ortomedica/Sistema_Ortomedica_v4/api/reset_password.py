import os, sys
from dotenv import load_dotenv
import mysql.connector
from passlib.context import CryptContext

# Uso: python api/reset_password.py epadilla@ortomedica.com "NuevaPass123!"
if len(sys.argv) < 3:
    print("Uso: python api/reset_password.py <email> <new_password>")
    sys.exit(1)

email = sys.argv[1].strip().lower()
new_password = sys.argv[2]

load_dotenv()

PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")

def db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST","127.0.0.1"),
        port=int(os.getenv("DB_PORT","3306")),
        user=os.getenv("DB_USER","root"),
        password=os.getenv("DB_PASS",""),
        database=os.getenv("DB_NAME","inventarios"),
    )

hash_ = PWD.hash(new_password)

con = db(); cur = con.cursor()
cur.execute("UPDATE users SET password_hash=%s, is_active=1 WHERE email=%s", (hash_, email))
con.commit()
cur.close(); con.close()
print("Contraseña actualizada para:", email)
