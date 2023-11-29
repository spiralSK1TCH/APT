import sqlite3
from getpass import getpass
import bcrypt
import datetime
filmDB = sqlite3.connect(".passwords.db")
c = filmDB.cursor()
while input("do you want to enter a record? (y/n) \t").lower() == "y":
    username = input("username\t").lower()
    password = getpass()
    salt = bcrypt.gensalt()
    encryptedPassword = str(bcrypt.hashpw(password.encode(), salt))
    date = datetime.datetime.now()
    c.execute(f'''INSERT INTO Passwords VALUES ("{username}","{encryptedPassword}","{date.strftime("%x")}")''')
    filmDB.commit()
filmDB.close()
input()
