import json
from flask import Flask, render_template, request, flash, jsonify, session, redirect, url_for
from crypto_utils import generate_aes_key, encrypt_aes, decrypt_aes
import os
import base64

app = Flask(__name__)

# settings
app.secret_key = 'mysecretkey'

# Ruta donde se guardará la clave AES
AES_KEY_FILE = 'aes_key.key'

# Verificar si ya existe la clave AES, sino generarla
if not os.path.exists(AES_KEY_FILE):
    aes_key = generate_aes_key()  # Generar la clave AES
    # Guardar la clave AES en un archivo seguro
    with open(AES_KEY_FILE, 'wb') as key_file:
        key_file.write(aes_key)
else:
    # Si ya existe, cargar la clave AES del archivo
    with open(AES_KEY_FILE, 'rb') as key_file:
        aes_key = key_file.read()

# web page
@app.route('/')
def index():
    return render_template('index.html')

# Route for rendering the registration form (GET)
@app.route('/register_form')
def register_form():
    return render_template('registro.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Validación de la contraseña (mayúsculas, números, caracteres especiales)
        mayusc = any(char.isupper() for char in password)
        number = any(char.isdigit() for char in password)
        special = any(not char.isalnum() for char in password)
        
        if len(password) < 8 or not mayusc or not number or not special:
            return jsonify(success=False, message="La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un caracter especial")
        
        # Generar la clave AES y encriptar la contraseña
        aes_key = generate_aes_key()  # Genera una clave AES única por usuario
        encrypted_password = encrypt_aes(aes_key, password)  # Encriptar la contraseña

        user_data = {
            'username': username,
            'email': email,
            'password': encrypted_password,
            'aes_key': base64.b64encode(aes_key).decode('utf-8')  # Guardar la clave AES en formato base64
        }

        json_file = 'usuarios_registrados.json'
        if os.path.exists(json_file):
            with open(json_file, 'r') as file:
                users = json.load(file)
                users.append(user_data)
        else:
            users = [user_data]

        with open(json_file, 'w') as file:
            json.dump(users, file, indent=4)

        return jsonify(success=True, message="Usuario registrado correctamente")


# Route for rendering the login form (GET)
@app.route('/login_form')
def login_form():
    return render_template('iniciosesion.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        json_file = 'usuarios_registrados.json'

        if os.path.exists(json_file):
            with open(json_file, 'r') as file:
                users = json.load(file)

            for user in users:
                if (user['username'] == username_or_email or user['email'] == username_or_email):
                    encrypted_password = user.get('password')
                    stored_aes_key = user.get('aes_key')

                    if not encrypted_password or not stored_aes_key:
                        flash("Error: No se encontró la contraseña o clave AES encriptada", "error")
                        return redirect(url_for('login_form'))

                    try:
                        # Decodificar la clave AES desde base64
                        aes_key = base64.b64decode(stored_aes_key)
                        decrypted_password = decrypt_aes(aes_key, encrypted_password)  # Desencriptar la contraseña

                        if decrypted_password == password:
                            session['username'] = user['username']
                            flash("Inicio de sesión correcto", "success")
                            return redirect(url_for('index'))
                        else:
                            flash("Contraseña incorrecta", "error")
                            return redirect(url_for('login_form'))

                    except Exception as e:
                        flash(f"Error al desencriptar la contraseña: {str(e)}", "error")
                        return redirect(url_for('login_form'))

            flash("Usuario o contraseña incorrectos", "error")
            return redirect(url_for('login_form'))
        else:
            flash("Error al leer la base de datos de usuarios", "error")
            return redirect(url_for('login_form'))



@app.route('/logout')
def logout():
    session.pop('username', None)  # Eliminar la sesión
    flash("Has cerrado sesión correctamente")
    return redirect(url_for('index'))

@app.route('/edit')
def edit_user():
    return 'Edit User'

@app.route('/delete')
def delete_user():
    return 'Delete User'

if __name__ == '__main__':
    app.run(port=3000, debug=True)

