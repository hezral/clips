

#This program reads passwords and adds their hash values to
#an SQLite application database.
#Michael, January 2014
#michael@ipv6secure.co.uk
#https://github.com/xerocrypt/Python/blob/master/Python-SQLite/AddHash.py

import sqlite3
import hashlib

#Connect to database
conn = sqlite3.connect('hashBase.db')

c = conn.cursor()

c.execute('''
    CREATE TABLE Hashes (
        user    TEXT        NOT NULL,
        hash    TEXT        NOT NULL
    );
    ''')

#Get username and password
currentUser = input("User name: ")
txtPassword = input("Password: ")

#Hash the user's password
currentPassword = hashlib.sha256(txtPassword.encode('utf-8')).hexdigest()

#Write entry to database table and commit
c.execute("insert into Hashes values (?, ?)", (currentUser, currentPassword))
conn.commit()

print("Password added.")

#Close connection to database
conn.close()