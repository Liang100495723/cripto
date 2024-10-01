from flask import Flask, request, jsonify
from authentication import register_user, authenticate_user
from encryption import encrypt_message
from digital_signature import verify_signature

app = Flask(__name__)

# Endpoint para el registro de usuarios
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    success, message = register_user(username, password)
    return jsonify({'message': message}), (200 if success else 400)

# Endpoint para la autenticación de usuarios
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    success, message = authenticate_user(username, password)
    return jsonify({'message': message}), (200 if success else 400)

# Endpoint para cifrar un mensaje
@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json()
    plaintext = data.get('plaintext')
    
    ciphertext = encrypt_message(plaintext)
    return jsonify({'ciphertext': ciphertext})

# Endpoint para verificar una firma digital
@app.route('/verify-signature', methods=['POST'])
def verify():
    data = request.get_json()
    data_to_verify = data.get('data')
    
    valid = verify_signature(data_to_verify)
    return jsonify({'verification': 'Firma válida' if valid else 'Firma no válida'})

if __name__ == '__main__':
    app.run(debug=True)
