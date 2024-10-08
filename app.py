import json
from flask import Flask, render_template, request, flash, jsonify
import os

app = Flask(__name__)

# settings
app.secret_key = 'mysecretkey'


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

        # Guardar en un archivo JSON local
        user_data = {
            'username': username,
            'password': password,
            'email': email
        }

        # Nombre del archivo JSON local
        json_file = 'usuarios_registrados.json'

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
        username_or_email = request.form['username or email']
        password = request.form['password']

        json_file = 'usuarios_registrados.json'

        if os.path.exists(json_file):
            # Leer el archivo JSON
            with open(json_file, 'r') as file:
                users = json.load(file)

            for user in users:
                if (user['username'] == username_or_email or user['email'] == username_or_email) and user['password'] == password:
                    flash("Inicio de sesión correcto")
                    return jsonify(success=True, message="Sesión iniciada correctamente")

            flash("Usuario o contraseña incorrectos")
            return jsonify(success=False, message="Error en el inicio de sesión")
        return jsonify(success=False, message="Error en el inicio de sesión")
        

@app.route('/edit')
def edit_user():
    return 'Edit User'

@app.route('/delete')
def delete_user():
    return 'Delete User'

if __name__ == '__main__':
    app.run(port=3000, debug=True)
