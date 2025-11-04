import os
from dotenv import load_dotenv
import mysql.connector
from passlib.context import CryptContext
from getpass import getpass

load_dotenv()

PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")

CFG = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASS", ""),
    database=os.getenv("DB_NAME", "inventarios"),
    port=int(os.getenv("DB_PORT", "3306")),
)

def get_connection():
    return mysql.connector.connect(**CFG)

def list_users():
    """Muestra todos los usuarios registrados"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT email, name, role, created_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    
    print("\n" + "="*80)
    print("USUARIOS REGISTRADOS".center(80))
    print("="*80 + "\n")
    
    for i, user in enumerate(users, 1):
        print(f"{i}. Email: {user[0]}")
        print(f"   Nombre: {user[1]}")
        print(f"   Rol: {user[2]}")
        print(f"   Creado: {user[3]}")
        print("-" * 80)
    
    cursor.close()
    conn.close()
    return users

def reset_password(email, new_password):
    """Cambia la contraseña de un usuario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si el usuario existe
    cursor.execute("SELECT email, name FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ No se encontró el usuario con email: {email}")
        cursor.close()
        conn.close()
        return False
    
    # Hash de la nueva contraseña
    hash_password = PWD.hash(new_password)
    
    # Actualizar contraseña
    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE email = %s",
        (hash_password, email)
    )
    conn.commit()
    
    print(f"\n✅ Contraseña actualizada exitosamente para: {user[1]} ({email})")
    
    cursor.close()
    conn.close()
    return True

def create_user(email, name, password, role='user'):
    """Crea un nuevo usuario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si ya existe
    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        print(f"❌ Ya existe un usuario con el email: {email}")
        cursor.close()
        conn.close()
        return False
    
    # Hash de la contraseña
    hash_password = PWD.hash(password)
    
    # Insertar usuario
    cursor.execute(
        "INSERT INTO users (email, name, password_hash, role) VALUES (%s, %s, %s, %s)",
        (email, name, hash_password, role)
    )
    conn.commit()
    
    print(f"\n✅ Usuario creado exitosamente: {name} ({email}) - Rol: {role}")
    
    cursor.close()
    conn.close()
    return True

def main_menu():
    """Menú interactivo"""
    while True:
        print("\n" + "="*80)
        print("GESTIÓN DE USUARIOS - ORTOMEDICA".center(80))
        print("="*80)
        print("\n1. Ver todos los usuarios")
        print("2. Cambiar contraseña de un usuario")
        print("3. Crear nuevo usuario")
        print("4. Salir")
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            list_users()
            
        elif opcion == "2":
            users = list_users()
            email = input("\nIngresa el email del usuario: ").strip().lower()
            new_password = getpass("Ingresa la nueva contraseña: ")
            confirm_password = getpass("Confirma la nueva contraseña: ")
            
            if new_password != confirm_password:
                print("❌ Las contraseñas no coinciden")
                continue
            
            if len(new_password) < 6:
                print("❌ La contraseña debe tener al menos 6 caracteres")
                continue
            
            reset_password(email, new_password)
            
        elif opcion == "3":
            print("\n--- CREAR NUEVO USUARIO ---")
            email = input("Email: ").strip().lower()
            name = input("Nombre: ").strip()
            password = getpass("Contraseña: ")
            confirm_password = getpass("Confirma la contraseña: ")
            
            if password != confirm_password:
                print("❌ Las contraseñas no coinciden")
                continue
            
            if len(password) < 6:
                print("❌ La contraseña debe tener al menos 6 caracteres")
                continue
            
            print("\nRoles disponibles:")
            print("1. admin - Administrador (acceso completo)")
            print("2. collab - Colaborador (acceso limitado)")
            print("3. user - Usuario básico")
            
            role_option = input("\nSelecciona el rol (1-3, default=3): ").strip() or "3"
            role_map = {"1": "admin", "2": "collab", "3": "user"}
            role = role_map.get(role_option, "user")
            
            create_user(email, name, password, role)
            
        elif opcion == "4":
            print("\n👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
