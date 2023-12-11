from re import search
import bcrypt
from getpass import getpass
import sqlite3
import os
import datetime
# Get Password & Encrypt


# Name hidden folder .passwords 
file = (".passwords")
Table = "Passwords" 

def setup():
    global c 
    global DB
    # If the file doesnt exist
    if not os.path.isfile(f"{file}.db"):
        # Create a new Database called passwords    
        print("Creating new database")
        DB = sqlite3.connect(f"{file}.db")
        c = DB.cursor()
        fieldNames = ("username", "password", "lastLogin")
       
        c.execute(f'''CREATE TABLE {Table}
        ( {fieldNames[0]} text
        , {fieldNames[1]} text
        , {fieldNames[2]} text)''')

        DB.commit()
        DB.close()
    DB = sqlite3.connect(f"{file}.db")
    c = DB.cursor()

def searchDB(search):
    c.execute(f'''SELECT username 
                  FROM {Table} 
                  WHERE username = "{search}"''')
    if c.fetchall(): return True

# Check entered password against the hash
def passwordCheckDB(username, password):
    # take the hashed password of the user
    c.execute(f'''SELECT password 
                  FROM {Table} 
                  WHERE username = "{username}"''')
    # Strip the data of quotation marks
    salt = str(c.fetchone()[0][2:-1])
    # compare the entered password with the sotred hash. if theyre equal,  return true 
    return bcrypt.checkpw(password.encode(), salt.encode())

# update the last login date
def updateDate(username):
    currentdate = datetime.datetime.now()
    c.execute(f'''UPDATE Passwords
                  SET lastLogin = {currentdate.strftime("%x")}
                  WHERE username = {username}''')
def addUser(username, password):
    salt = bcrypt.gensalt()
    encryptedPassword = str(bcrypt.hashpw(password.encode(), salt))
    date = datetime.datetime.now()
    c.execute(f'''INSERT INTO Passwords VALUES ("{username}","{encryptedPassword}","{date.strftime("%x")}")''')
    DB.commit()

def closeDB():
    DB.commit()
    DB.close()


