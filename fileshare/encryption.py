from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
import hashlib
import os

# Generate RSA keys (only once for demo)
if not os.path.exists("private.pem") or not os.path.exists("public.pem"):
    key = RSA.generate(2048)

    with open("private.pem", "wb") as private_file:
        private_file.write(key.export_key())

    with open("public.pem", "wb") as public_file:
        public_file.write(key.publickey().export_key())


def generate_hash(file_data):
    return hashlib.sha256(file_data).hexdigest()


def encrypt_file(file_data):
    aes_key = os.urandom(16)

    cipher_aes = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(file_data)

    with open("public.pem", "rb") as f:
        public_key = RSA.import_key(f.read())

    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)

    return encrypted_aes_key + cipher_aes.nonce + tag + ciphertext


def decrypt_file(encrypted_data):
    encrypted_aes_key = encrypted_data[:256]
    nonce = encrypted_data[256:272]
    tag = encrypted_data[272:288]
    ciphertext = encrypted_data[288:]

    with open("private.pem", "rb") as f:
        private_key = RSA.import_key(f.read())

    cipher_rsa = PKCS1_OAEP.new(private_key)
    aes_key = cipher_rsa.decrypt(encrypted_aes_key)

    cipher_aes = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)

    return cipher_aes.decrypt_and_verify(ciphertext, tag)