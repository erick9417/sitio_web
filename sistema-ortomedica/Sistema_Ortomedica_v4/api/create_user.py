import os
from dotenv import load_dotenv
import mysql.connector
from passlib.context import CryptContext

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

email = "epadilla@ortomedica.com"
name = "EPN"
role = "admin"
password = "password123"  # cámbiala

con = db(); cur = con.cursor()
cur.execute("INSERT INTO users (email,password_hash,name,role) VALUES (%s,%s,%s,%s)",
            (email, PWD.hash(password), name, role))
con.commit()
cur.close(); con.close()
print("Usuario creado:", email)
