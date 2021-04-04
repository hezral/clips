#This program checks a username and password against an SQLite database
#Michael, January 2014
#michael@ipv6secure.co.uk
#https://github.com/xerocrypt/Python/blob/master/Python-SQLite/CheckPassword.py

import sqlite3
import hashlib

#Connect to database
conn = sqlite3.connect('hashBase.db')
c = conn.cursor()

#Read entered password and generate hash
currentUser = raw_input("Login: ")
currentPass = raw_input("Enter password: ")
currentHash = hashlib.sha256(currentPass).hexdigest()

#Read entry in database and get password hash
t = (currentUser,)
c.execute('SELECT Hash FROM Hashes WHERE Username=?', t)

#Run if user account exists in database
row = c.fetchone()
if row is None:
	print "Account not found"
else:
	fetchedHash = row[0]

	#Compare currentHash with entry from database
	if fetchedHash == currentHash:
		print "Login Success."
	else:
		print "Login Fail."