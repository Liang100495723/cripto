import json
from flask import Flask, render_template, request, flash, jsonify, session, redirect, url_for
from crypto_utils import generate_aes_key, encrypt_aes, decrypt_aes, load_public_key, load_private_key, encrypt_rsa, decrypt_rsa, generate_hmac, verify_hmac
import os
import base64
from Crypto.Cipher import AES

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
        hmac_generado = generate_hmac(aes_key, password)
        print(f"MAC generado: {hmac_generado}")
        print(f"Algoritmo: HMAC-SHA-256, Longitud de clave: {len(aes_key)*8} bits")
        es_valido = verify_hmac(aes_key, password, hmac_generado)
        print(f"El HMAC es válido: {'Sí' if es_valido else 'No'}")

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
            'aes_key': base64.b64encode(aes_key).decode('utf-8'),  # Guardar la clave AES en formato base64
            'hmac_generado': hmac_generado
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
                    stored_hmac = user.get('hmac_generado')
                    encrypted_password = user.get('password')
                    stored_aes_key = user.get('aes_key')
                    if not encrypted_password or not stored_aes_key:
                        flash("Error: No se encontró la contraseña o clave AES encriptada", "error")
                        return redirect(url_for('login_form'))
                    try:
                        # Decodificar la clave AES desde base64
                        aes_key = base64.b64decode(stored_aes_key)
                        decrypted_password = decrypt_aes(aes_key, encrypted_password)  # Desencriptar la contraseña
                        if decrypted_password == password and verify_hmac(aes_key, password, stored_hmac):
                            print(f"Algoritmo: HMAC-SHA-256, Longitud de clave: {len(aes_key)*8} bits")
                            print(f"El HMAC es válido")
                            session['username'] = user['username']
                            session['email'] = user['email'] #Guardamos el email para enviar lo de la carta
                            session['aes_key'] = user['aes_key']
                            flash("Inicio de sesión correcto", "success")
                            # Return JSON success response for AJAX
                            #Nos aseguramos de que el JSON con cartas NUNCA esté disponible si no eres papá noel
                            if session['username'] != 'PAPA NOEL':
                                # Elimina el archivo 'cartas_descifradas.json' si existe
                                if os.path.exists('cartas_descifradas.json'):
                                    os.remove('cartas_descifradas.json')
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
    if session.get('username') == 'PAPA NOEL':
        # Elimina el archivo 'cartas_descifradas.json' si existe
        if os.path.exists('cartas_descifradas.json'):
            os.remove('cartas_descifradas.json')
    session.pop('username', None)  # Elimina la sesión
    session.pop('email', None) #Elimina el email
    flash("Has cerrado sesión correctamente")
    return redirect(url_for('index'))

@app.route('/enviar-carta', methods=['POST'])
def enviar_carta():
    # Obtener los datos del formulario
    nombre = request.form['nombre']
    email = request.form['email']
    ciudad = request.form['ciudad']
    pais = request.form['pais']
    carta = request.form['carta']

    if session.get('email') is None or email != session.get('email'):
        return jsonify(success=False, message="Sesión o email no coinciden")

    public_key = load_public_key()
    aes_key = base64.b64decode(session['aes_key'])
    print(f"Clave usada para generar el hmac: {aes_key}")
    print(f"Carta: {carta}")
    hmac_generado = generate_hmac(aes_key, carta)
    print(f"HMAC generado: {hmac_generado}")
    print(f"Algoritmo: HMAC-SHA-256, Longitud de clave: {len(aes_key)*8} bits")
    #es_valido = verify_hmac(carta, aes_key, hmac_generado)
    #print(f"El HMAC es válido: {'Sí' if es_valido else 'No'}")
    carta_cifrada = encrypt_aes(aes_key, carta)
    aes_key_cifrada = encrypt_rsa(public_key, base64.b64encode(aes_key).decode())
    
    

    cartas_data = {
        'nombre': nombre,
        'email': email,
        'ciudad': ciudad,
        'pais': pais,
        'carta': carta_cifrada,
        'aes_key_cifrada': aes_key_cifrada,
        'hmac_generado': hmac_generado
    }

    json_file = 'cartas_usuarios.json'

    # Verifica si el archivo JSON contiene una lista válida
    if os.path.exists(json_file) and os.path.getsize(json_file) > 0:
        with open(json_file, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []  # Inicia una lista vacía si el archivo tiene un formato inválido
    else:
        data = []

    data.append(cartas_data)

    # Guarda el archivo JSON con el nuevo dato incluido
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

    return jsonify(success=True, message="Carta enviada correctamente :)")

# TODO: no se popea las cartas que son descifradas :/
# Ruta para mostrar la página para subir la clave privada
@app.route('/leer-cartas')
def leer_cartas_form():
    return render_template('leer_cartas.html')

# Ruta para que Papá Noel lea las cartas (descifrado RSA)
@app.route('/leer-cartas-descifradas', methods=['GET'])
def leer_cartas():
    print("Leyendo cartas")
    private_key = load_private_key()  # Asegúrate de que la clave privada esté disponible

    json_file = 'cartas_usuarios.json'
    if not os.path.exists(json_file):
        # Si no existe el archivo, devolver un mensaje de error en JSON
        return jsonify({"error": "No hay cartas disponibles"}), 404

    # Leer y procesar cartas
    with open(json_file, 'r') as file:
        cartas = json.load(file)

    cartas_descifradas = []
    for carta in cartas:
        try:
            aes_key_cifrada = carta['aes_key_cifrada']
            aes_key_descifrada = decrypt_rsa(private_key, aes_key_cifrada)
            aes_key_bytes = base64.b64decode(aes_key_descifrada)

            
            carta_cifrada_data = json.loads(carta['carta'])
            stored_hmac = carta['hmac_generado']
            ciphertext = base64.b64decode(carta_cifrada_data['ciphertext'])
            
            nonce = base64.b64decode(carta_cifrada_data['nonce'])
            tag = base64.b64decode(carta_cifrada_data['tag'])

            cipher = AES.new(aes_key_bytes, AES.MODE_GCM, nonce=nonce)
            carta_descifrada = cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

            cartas_descifradas.append({
                'nombre': carta['nombre'],
                'email': carta['email'],
                'ciudad': carta['ciudad'],
                'pais': carta['pais'],
                'carta': carta_descifrada
            })

            if not verify_hmac(aes_key_bytes, carta_descifrada, stored_hmac):
                print(f"El HMAC no puede verificarse. Es posible que la carta haya sido alterada")
            else:
                print(f"Algoritmo: HMAC-SHA-256, Longitud de clave: {len(aes_key_bytes)*8} bits")
                print(f"El HMAC es válido")

        except Exception as e:
            print(f"Error al descifrar la carta: {e}")

    # Guardar las cartas descifradas en un archivo JSON
    if cartas_descifradas:
        with open('cartas_descifradas.json', 'w') as output_file:
            json.dump(cartas_descifradas, output_file, indent=4)
        print("Cartas descifradas guardadas en cartas_descifradas.json")
    else:
        print("No se pudieron descifrar las cartas")

    # Devolver las cartas descifradas como JSON
    return jsonify(cartas_descifradas)  # Devolver el JSON





if __name__ == '__main__':
    app.run(port=3000, debug=True)

