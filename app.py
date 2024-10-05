from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Connection
# la ruta de mysql si tienes
# 1. windows:
# app.config['MYSQL_HOST'] = 'localhost'
# 2. linux:
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'lab_criptografia'
mysql = MySQL(app)

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

@app.route('/register', methods = ['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO usuarios_registrados (username, password, email) VALUES (%s, %s, %s)',
                    (username, password, email))
        mysql.connection.commit()
        flash("Usuario registrado correctamente")
        return jsonify(success=True, message="Usuario registrado correctamente")
    return jsonify(success=False, message="Error en el registro")

@app.route('/login')
def login():
    return 'Login'

@app.route('/edit')
def edit_user():
    return 'Edit User'

@app.route('/delete')
def delete_user():
    return 'Delete User'

if __name__ == '__main__':
    app.run(port = 3000, debug = True)
