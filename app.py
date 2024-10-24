import json
from flask import Flask, render_template, request, flash, jsonify, session, redirect, url_for
from crypto_utils import generate_aes_key, encrypt_aes, decrypt_aes, load_public_key, load_private_key, encrypt_rsa, decrypt_rsa
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

        # Requisitos para la creación de la contraseña, aún NO se encripta nada
        # Validación de la contraseña (mayúsculas, números, caracteres especiales)
        mayusc = any(char.isupper() for char in password)
        number = any(char.isdigit() for char in password)
        special = any(not char.isalnum() for char in password)

        if len(password) < 8 or not mayusc or not number or not special:
            return jsonify(success=False,
                           message="La contraseña debe tener al menos 8 caracteres, una mayúscula, un número y un caracter especial")

        # Generar la clave AES y encriptar la contraseña
        aes_key = generate_aes_key()  # Genera una clave AES única por usuario
        encrypted_password = encrypt_aes(aes_key, password)  # Encriptar la contraseña

        # Archivo json
        json_file = 'usuarios_registrados.json'

        if os.path.exists(json_file):
            # Leer el archivo JSON
            with open(json_file, 'r') as file:
                users = json.load(file)

            # Si existe ya el usuario salta error:
            for user in users:
                if user['username'] == username:
                    return jsonify(success=False, message="El nombre de usuario ya existe")
                if user['email'] == email:
                    return jsonify(success=False, message="El correo electrónico ya está registrado")

        # Guardar en un archivo JSON local
        user_data = {
            'username': username,
            'email': email,
            'password': encrypted_password,
            'aes_key': base64.b64encode(aes_key).decode('utf-8')  # Guardar la clave AES en formato base64
        }

        # Verificar si el archivo existe
        if os.path.exists(json_file):
            # Si existe, leer el archivo y agregar el nuevo usuario
            with open(json_file, 'r') as file:
                data = json.load(file)
                data.append(user_data)
        else:
            # Si no existe, crear una nueva lista con el primer usuario
            data = [user_data]

        # Guardar el archivo actualizado
        with open(json_file, 'w') as file:
            json.dump(data, file, indent=4)

        flash("Usuario registrado correctamente")
        return jsonify(success=True, message="Usuario registrado correctamente")

    return jsonify(success=False, message="Error en el registro")


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
            # Leer el archivo JSON
            with open(json_file, 'r') as file:
                users = json.load(file)

            # Validar usuario o email con la contraseña
            for user in users:
                if user['username'] == username_or_email or user['email'] == username_or_email:
                    encrypted_password = user.get('password')
                    stored_aes_key = user.get('aes_key')
                    if not encrypted_password or not stored_aes_key:
                        flash("Error: No se encontró la contraseña o clave AES encriptada", "error")
                        return redirect(url_for('login_form'))
                    try:
                        # Decodificar la clave AES desde base64
                        aes_key = base64.b64decode(stored_aes_key)
                        decrypted_password = decrypt_aes(aes_key, encrypted_password)  # Desencriptar la contraseña
                        print(decrypted_password)
                        if decrypted_password == password:
                            session['username'] = user['username']
                            session['email'] = user['email'] #Guardamos el email para enviar lo de la carta
                            session['aes_key'] = user['aes_key']
                            flash("Inicio de sesión correcto", "success")
                            # Return JSON success response for AJAX
                            return jsonify(success=True, username=user['username'],
                                           avatar_url=None)  # Assuming no avatar for now
                        else:
                            flash("Contraseña incorrecta", "error")
                            return jsonify(success=False, message="Contraseña incorrecta")
                    except Exception as e:
                        flash(f"Error al desencriptar la contraseña: {str(e)}", "error")
                        return redirect(url_for('login_form'))
                # Si no coincide el usuario/email o contraseña
            flash("Usuario incorrecto", "error")
            return jsonify(success=False, message="Usuario incorrecto")
        else:
            return jsonify(success=False, message="Error al leer la base de datos de usuarios")


@app.route('/logout')
def logout():
    session.pop('username', None)  # Elimina la sesión
    session.pop('email', None) #Elimina el email
    flash("Has cerrado sesión correctamente")
    return redirect(url_for('index'))

# TODO: el pop up arreglarlo porfis jajajaj
# Ruta para enviar carta (cifrado RSA)
@app.route('/enviar-carta', methods=['POST'])
def enviar_carta():
    # Obtener los datos del formulario
    nombre = request.form['nombre']
    email = request.form['email']
    ciudad = request.form['ciudad']
    pais = request.form['pais']
    carta = request.form['carta']

    
    # Verificar que el usuario esté autenticado
    if session.get('email') is None:
        return jsonify(success=False, message="Por favor, inicia sesión para enviar una carta")
    if not nombre or not email or not ciudad or not pais or not carta:
        return jsonify(success=False, message="Por favor, complete todos los campos")
    if email != session.get('email'):
        return jsonify(success=False, message="El email no coincide con el del usuario logueado")

    # Cargar la clave pública de Papá Noel
    public_key = load_public_key()
    #HAY QUE CIFRAR LA CARTA CON AES Y LA CONTRASEÑA DEL AES CON LA CLAVE PUBLICA DE PAPA NOEL
    # Cifrar la carta usando RSA
    try:
        aeskey = session.get('aes_key')
        aeskey_decoded = base64.b64decode(aeskey)
        print("estoy aquí")
        carta_cifrada = encrypt_aes(aeskey_decoded, carta)
        print("holaaaa")
        aeskey_cifrada = encrypt_rsa(public_key, base64.b64encode(aes_key).decode('utf-8'))
        print(aeskey_cifrada)
    except Exception as e:
        return jsonify(success=False, message=f"Error al cifrar la carta: {str(e)}")
    # Path al archivo JSON
    json_file = 'cartas_usuarios.json'
    
    # Data que se va a agregar al archivo JSON
    cartas_data = {
        'nombre': nombre,
        'email': email,
        'ciudad': ciudad,
        'pais': pais,
        'carta': carta_cifrada,  # Guardar la carta cifrada
        'aes_key_cifrada': aeskey_cifrada # Guardar la clave AES cifrada con RSA
    }

    # Verifica si el archivo JSON existe
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r') as file:
                file_content = file.read().strip()  # Leer y eliminar espacios en blanco
                
                if file_content:  # Si el archivo tiene contenido
                    data = json.loads(file_content)
                else:
                    data = []  # Si está vacío, inicializar como una lista vacía
        except json.JSONDecodeError:
            # Manejar el caso en el que el JSON esté mal formado
            data = []
    else:
        data = []  # Si no existe, inicializa con una lista vacía

    # Agregar la nueva carta cifrada a los datos existentes
    data.append(cartas_data)

    # Guardar los datos actualizados en el archivo JSON
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

    # Flash message y respuesta JSON
    flash("Carta enviada correctamente :)")
    return jsonify(success=True, message="Carta enviada correctamente :)")

# TODO: Lectura cartas papa noel?
# Ruta para mostrar la página para subir la clave privada
@app.route('/leer-cartas')
def leer_cartas_form():
    return render_template('leer_cartas.html')

# Ruta para que Papá Noel lea las cartas (descifrado RSA)
@app.route('/leer-cartas', methods=['GET'])
def leer_cartas():
    # Cargar la clave privada de Papá Noel
    private_key = load_private_key()

    json_file = 'cartas_usuarios.json'
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            cartas = json.load(file)
    else:
        return jsonify(success=False, message="No hay cartas disponibles")

    # Descifrar las cartas
    cartas_descifradas = []
    for carta in cartas:
        try:
            carta_descifrada = decrypt_rsa(private_key, carta['carta'])
            cartas_descifradas.append({
                'nombre': carta['nombre'],
                'email': carta['email'],
                'ciudad': carta['ciudad'],
                'pais': carta['pais'],
                'carta': carta_descifrada
            })
        except Exception as e:
            print(f"Error al descifrar la carta: {e}")

    return jsonify(success=True, cartas=cartas_descifradas)

if __name__ == '__main__':
    app.run(port=3000, debug=True)

