import json
from flask import Flask, render_template, request, flash, jsonify, session, redirect, url_for
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

        # Requisitos para la creación de la contraseña, aún NO se encripta nada
        mayusc = False
        number = False
        special = False

        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres")
            return jsonify(success=False, message="La contraseña debe tener al menos 8 caracteres")
        for char in password:
            if char.isupper():
                mayusc = True
            elif char.isdigit():
                number = True
            elif not char.isalnum():
                special = True
        
        if not mayusc or not number or not special:
            return jsonify(success=False, message="La contraseña debe contener al menos una mayúscula, un número y un caracter especial")
        
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
            'password': password,
            'email': email
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

            for user in users:
                if (user['username'] == username_or_email or user['email'] == username_or_email) and user['password'] == password:
                    # Guardar el nombre de usuario en la sesión
                    session['username'] = user['username']
                    flash("Inicio de sesión correcto", "success")
                    
                    # Redirigir a la página de inicio con la sesión activa
                    return redirect(url_for('index'))

            flash("Usuario o contraseña incorrectos", "error")
            return redirect(url_for('login_form'))
        else:
            flash("Error al leer la base de datos de usuarios", "error")
            return redirect(url_for('login_form'))


@app.route('/logout')
def logout():
    session.pop('username', None)  # Elimina la sesión
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
