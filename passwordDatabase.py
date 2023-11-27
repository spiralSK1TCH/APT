import bcrypt
from getpass import getpass
import sqlite3


# Get Password & Encrypt
masterKey = getpass()
salt = bcrypt.gensalt()
encryptedPassword = bcrypt.hashpw(masterKey.encode(), salt)

class PasswordDatab

