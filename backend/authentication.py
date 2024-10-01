import os
import json
import hashlib

# Ruta al archivo JSON donde se almacenan los usuarios
USERS_FILE = 'data/users.json'

# Función para cargar los datos del archivo JSON
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}  # Si no existe el archivo, retornamos un diccionario vacío
    with open(USERS_FILE, 'r') as file:
        return json.load(file)

# Función para guardar los datos en el archivo JSON
def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

# Función para hashear la contraseña
def hash_password(password):
    salt = os.urandom(16)
    hashed_pw = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt + hashed_pw  # Almacenamos la sal junto con la contraseña hasheada

# Función para verificar la contraseña proporcionada
def verify_password(stored_password, provided_password):
    salt = stored_password[:16]
    stored_hash = stored_password[16:]
    provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
    return stored_hash == provided_hash

# Función para registrar un nuevo usuario
def register_user(username, password):
    users = load_users()
    
    if username in users:
        return False, "Usuario ya registrado"
    
    # Hasheamos la contraseña y guardamos el usuario en el archivo JSON
    users[username] = hash_password(password).hex()
    save_users(users)
    return True, "Usuario registrado con éxito"

# Función para autenticar un usuario
def authenticate_user(username, password):
    users = load_users()
    
    if username not in users:
        return False, "Usuario no encontrado"
    
    stored_password = bytes.fromhex(users[username])
    
    if verify_password(stored_password, password):
        return True, "Autenticación exitosa"
    
    return False, "Contraseña incorrecta"
