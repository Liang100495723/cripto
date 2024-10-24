from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
import os
import base64
import json
import hmac
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# Symmetric Encryption (AES)
def generate_aes_key():
    return get_random_bytes(32)  # AES-256 key

def encrypt_aes(key, data):
    print("encrypt_aes")
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    
    encrypted_data = {
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
        'nonce': base64.b64encode(cipher.nonce).decode('utf-8'),
        'tag': base64.b64encode(tag).decode('utf-8')
    }
    return json.dumps(encrypted_data)

def decrypt_aes(key, encrypted_data):
    encrypted_data = json.loads(encrypted_data)
    nonce = base64.b64decode(encrypted_data['nonce'])
    ciphertext = base64.b64decode(encrypted_data['ciphertext'])
    tag = base64.b64decode(encrypted_data['tag'])

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

# Asymmetric Encryption (RSA)
# Cargar la clave pública de Papá Noel
def load_public_key():
    with open("papanoel_public_key.pem", "rb") as key_file:
        public_key = load_pem_public_key(key_file.read(), backend=default_backend())
    return public_key

# Cargar la clave privada de Papá Noel (para descifrar cartas)
def load_private_key():
    with open("papanoel_private_key.pem", "rb") as key_file:
        private_key = load_pem_private_key(key_file.read(), password=None, backend=default_backend())
    return private_key

# Función para cifrar usando RSA
def encrypt_rsa(public_key, message):
    encrypted = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return base64.b64encode(encrypted).decode()

# Función para descifrar usando RSA
def decrypt_rsa(private_key, encrypted_message):
    decrypted = private_key.decrypt(
        base64.b64decode(encrypted_message),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted.decode()

# HMAC for Authentication
def generate_hmac(secret_key, message):
    h = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256)
    return h.hexdigest()

def verify_hmac(secret_key, message, received_hmac):
    generated_hmac = generate_hmac(secret_key, message)
    return hmac.compare_digest(generated_hmac, received_hmac)
