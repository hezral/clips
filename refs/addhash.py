

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

#Get username and password
currentUser = raw_input("User name: ")
txtPassword = raw_input("Password: ")

#Hash the user's password
currentPassword = hashlib.sha256(txtPassword).hexdigest()

#Write entry to database table and commit
c.execute("insert into Hashes values (?, ?)", (currentUser, currentPassword))
conn.commit()

print "Password added."

#Close connection to database
conn.close()