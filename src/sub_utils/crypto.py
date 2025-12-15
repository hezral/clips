import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from hashlib import sha1
import base64
import os

def do_encryption(action, passphrase, filepath):
    def key_func(action, passphrase, filepath):
        password = passphrase.encode()
        if action == "encrypt":
            salt = os.urandom(16)
        else:
            with open(filepath, 'rb') as file:
                salt = file.read(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key, salt

    def encrypt(key, salt, filepath):
        fernet = Fernet(key)
        file, ext = os.path.splitext(filepath)
        file = file.split('\\' or '/')[-1]
        encrypted_file = file + "_enc_" + ext

        with open(filepath, 'rb') as file:
            original = file.read()

        try:
            data = fernet.encrypt(original)
            with open(encrypted_file, 'wb') as file:
                file.write(salt)
                file.write(data)
            return True, encrypted_file
        except:
            return False, "encryption failed"
        
    def decrypt(key, filepath):
        fernet = Fernet(key)
        file, ext = os.path.splitext(filepath)
        file = file.split('\\' or '/')[-1]

        with open(filepath, 'rb') as file:
            data = file.read()
        data = data[16:]

        try:
            return True, fernet.decrypt(data)
        except cryptography.fernet.InvalidToken as error:
            return False, "decryption failed {errormsg}".format(errormsg=error)

    encryption_key, salt = key_func(action, passphrase, filepath)
    
    if action == "encrypt":
        return encrypt(encryption_key, salt, filepath)

    if action == "decrypt":
        return decrypt(encryption_key, filepath)
