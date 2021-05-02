import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from hashlib import sha1
import getpass
import base64
import os
import argparse

# all arguments
arg_parser = argparse.ArgumentParser(prog='Enc-Dec', usage='%(prog)s [options]')
arg_parser.add_argument('-f', '--file', type=str, help='File name', required=True, metavar='')
arg_parser.add_argument('-r', '--rename', type=bool, help='Rename the file', default=False, metavar='')
arg_parser.add_argument('-d', '--delete', type=bool, help='Delete unencrypted file', default=False, metavar='')
arg_parser.add_argument('-a', '--action', type=str, help='enc or dec', required=True, metavar='')

args = arg_parser.parse_args()
input_file = args.file

def key_func(input_file=None):
    # creates key for encryption or takes key for decryption.
    pw = getpass.getpass("enter key: ")
    # makes the string readable for fernet.
    password = pw.encode()
    
    # salt = b'salt_'
    if input_file is None:
        salt = os.urandom(16)
    else:
        with open(input_file, 'rb') as file:
            salt = file.read(16)
    print(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    # ctrl+v
    return key, salt


def encrypt(key, salt, input_file):
    fernet = Fernet(key)
    file, ext = os.path.splitext(input_file)
    file = file.split('\\' or '/')[-1]

    encrypted_name = file + "_enc" + ext
    with open(input_file, 'rb') as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    # deletes the unencrypted file if --delete/-d is True.(default=False)
    # os.remove(input_file)

    with open(encrypted_name, 'wb') as file:
        file.write(salt)
        file.write(encrypted)

def decrypt(key, input_file):
    fernet = Fernet(key)
    file, ext = os.path.splitext(input_file)
    file = file.split('\\' or '/')[-1]

    decrypted_name = file + "_dec" + ext

    with open(input_file, 'rb') as file:
        encrypted_file = file.read()
    
    encrypted_file = encrypted_file[16:]

    try:
        decrypted = fernet.decrypt(encrypted_file)
        
        print(decrypted.decode('utf-8'))

        # with open(decrypted_name, 'wb') as file:
        #     file.write(decrypted[16:])

    except cryptography.fernet.InvalidToken:
        print('Wrong password')

if __name__ == "__main__":
    # key_pass, salt = key_func()
    if args.action == 'enc':
        key_pass, salt = key_func()
        encrypt(key_pass, salt, args.file)
    elif args.action == 'dec':
        key_pass, salt = key_func(args.file)
        decrypt(key_pass, args.file)
