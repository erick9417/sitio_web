import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

# Configuración de la base de datos
CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "inventarios"),
    port=int(os.getenv("DB_PORT", "3306")),
)

try:
    # Conectar a la base de datos
    conn = mysql.connector.connect(**CFG)
    cursor = conn.cursor()
    
    print("✅ Conexión exitosa a MySQL\n")
    
    # Verificar tablas existentes
    print("=== TABLAS EN LA BASE DE DATOS ===")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")
    
    print("\n" + "="*50 + "\n")
    
    # Intentar obtener usuarios
    try:
        cursor.execute("SELECT email, role, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        if users:
            print("=== USUARIOS REGISTRADOS ===\n")
            for user in users:
                print(f"Email: {user[0]}")
                print(f"Rol: {user[1]}")
                print(f"Creado: {user[2]}")
                print("-" * 50)
            print(f"\nTotal de usuarios: {len(users)}")
        else:
            print("ℹ️ No hay usuarios registrados.")
    except mysql.connector.Error as e:
        print(f"❌ Error al consultar usuarios: {e}")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f"❌ Error de conexión a MySQL: {e}")
    print(f"\nConfiguración utilizada:")
    print(f"  Host: {CFG['host']}")
    print(f"  Port: {CFG['port']}")
    print(f"  User: {CFG['user']}")
    print(f"  Database: {CFG['database']}")
except Exception as e:
    print(f"❌ Error inesperado: {e}")
