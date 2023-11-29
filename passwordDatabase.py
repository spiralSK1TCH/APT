from re import search
import bcrypt
from getpass import getpass
import sqlite3
import os

# Get Password & Encrypt


# Name hidden folder .passwords 
file = (".passwords")
Table = "Passwords" 

def setup():
    global c 
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

def passwordCheckDB(username, password):
    c.execute(f'''SELECT password 
                  FROM {Table} 
                  WHERE username = "{username}"''')
    salt = str(c.fetchone()[0][2:-1])
    return bcrypt.checkpw(password.encode(), salt.encode())
     


