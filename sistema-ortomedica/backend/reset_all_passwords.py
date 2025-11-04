import os
from dotenv import load_dotenv
import mysql.connector
from passlib.hash import bcrypt

load_dotenv()

CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "inventarios"),
    port=int(os.getenv("DB_PORT", "3306")),
)

def get_connection():
    return mysql.connector.connect(**CFG)

print("="*80)
print("RESETEAR CONTRASEÑAS DE USUARIOS".center(80))
print("="*80 + "\n")

# Listar usuarios
conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT email, name, role FROM users ORDER BY created_at DESC")
users = cursor.fetchall()

print("Usuarios disponibles:\n")
for i, user in enumerate(users, 1):
    print(f"{i}. {user[0]} - {user[1]} ({user[2]})")

cursor.close()
conn.close()

print("\n" + "="*80)
print("\nEstableciendo contraseña '123456' para TODOS los usuarios...")
print("="*80 + "\n")

# Nueva contraseña para todos
new_password = "123456"
hash_password = bcrypt.hash(new_password)

conn = get_connection()
cursor = conn.cursor()

for user in users:
    email = user[0]
    cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hash_password, email))
    print(f"✅ Contraseña actualizada para: {email}")

conn.commit()
cursor.close()
conn.close()

print("\n" + "="*80)
print("RESUMEN".center(80))
print("="*80)
print(f"\n✅ Se actualizaron {len(users)} usuarios")
print(f"🔑 Nueva contraseña para todos: {new_password}")
print("\nPuedes iniciar sesión con cualquiera de estos usuarios usando la contraseña: 123456\n")
