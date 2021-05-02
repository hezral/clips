import gi
gi.require_version('Handy', '1')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Handy, GdkPixbuf

# functions to encrypt or decrypt files
def do_encryption(button, action, passphrase, filepath, label_widget):
    import cryptography
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from hashlib import sha1
    import base64
    import os

    passphrase = passphrase.props.text
    filepath = filepath.props.text

    print(action, passphrase, filepath)

    def key_func(passphrase, filepath):
        # makes the string readable for fernet.
        password = passphrase.encode()
        if filepath is None:
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
        encrypted_name = file + "_enc" + ext

        with open(filepath, 'rb') as file:
            original = file.read()

        try:
            encrypted = fernet.encrypt(original)
            # os.remove(filepath)
            with open(encrypted_name, 'wb') as file:
                file.write(salt)
                file.write(encrypted)
            return True
        except:
            print("Encryption failed")
            return False
        
    def decrypt(key, filepath):
        fernet = Fernet(key)
        file, ext = os.path.splitext(filepath)
        file = file.split('\\' or '/')[-1]
        # decrypted_name = file + "_dec" + ext

        with open(filepath, 'rb') as file:
            encrypted_file = file.read()
        encrypted_file = encrypted_file[16:]

        try:
            decrypted = fernet.decrypt(encrypted_file)
            # print(decrypted.decode('utf-8'))
            label_widget.props.label = decrypted.decode('utf-8')
            # with open(decrypted_name, 'wb') as file:
            #     file.write(decrypted)
            return True
        except cryptography.fernet.InvalidToken:
            print("Decryption failed")
            return False

    if action == "encrypt":
        encryption_key, salt = key_func(passphrase, filepath)
        encrypt(encryption_key, salt, filepath)

    if action == "decrypt":
        encryption_key, salt = key_func(passphrase, filepath)
        decrypt(encryption_key, filepath)

def print_password(entry, label):
    label.props.label = entry.props.text

def print_entry(button):
    print(entry2.props.text, entry1.props.text)

def do_set_icon1(button, win):
    win.set_icon(GdkPixbuf.Pixbuf.new_from_file('/usr/share/icons/elementary/apps/48/system-os-install.svg'))

def do_set_icon2(button, win):
    win.set_icon(GdkPixbuf.Pixbuf.new_from_file('/usr/share/icons/elementary/apps/48/web-browser.svg'))

header = Gtk.HeaderBar()
header.props.show_close_button = True
header.props.title = "GtkWindow"

label = Gtk.Label()
label.props.label = "TEST"
label.props.expand = True
label.props.valign = label.props.halign = Gtk.Align.CENTER

entry1 = Gtk.Entry()
entry1.props.input_purpose = Gtk.InputPurpose.PASSWORD
entry1.props.visibility = False
entry1.props.expand = True
entry1.props.valign = entry1.props.halign = Gtk.Align.FILL
entry1.connect("activate", print_password, label)

entry2 = Gtk.Entry()
entry2.props.expand = True
entry2.props.valign = entry2.props.halign = Gtk.Align.FILL

encrypt_button = Gtk.Button(label="Encrypt")
decrypt_button = Gtk.Button(label="Decrypt")

grid = Gtk.Grid()
grid.props.expand = True
grid.props.margin = 10
grid.props.column_spacing = grid.props.row_spacing = 6
grid.attach(entry1, 0, 1, 1, 1)
grid.attach(entry2, 0, 2, 1, 1)
grid.attach(label, 0, 3, 1, 1)
grid.attach(encrypt_button, 0, 4, 1, 1)
grid.attach(decrypt_button, 0, 5, 1, 1)

win = Gtk.Window()
win.set_size_request(400,250)
win.get_style_context().add_class("rounded")
win.set_titlebar(header)
win.add(grid)

win.show_all()
win.connect("destroy", Gtk.main_quit)
encrypt_button.connect("clicked", do_encryption, "encrypt", entry1, entry2, label)
encrypt_button.connect("clicked", do_set_icon1, win)
decrypt_button.connect("clicked", do_encryption, "decrypt", entry1, entry2, label)
decrypt_button.connect("clicked", do_set_icon2, win)

Gtk.main()



