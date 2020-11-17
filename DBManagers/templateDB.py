from flask import Flask
from hashlib import sha224
from flask_mysql_connector import MySQL
from mysql.connector.errors import IntegrityError
import sys
import json

app = Flask(__name__)

mysql = MySQL(app)

def getPromo(id:int, columns:list ):
    q = f"SELECT {', '.join(columns)} FROM promos WHERE id = %s "
    cur = mysql.connection.cursor(dictionary=True)
    cur.execute(q, [id])
    res= cur.fetchone()
    return res

    

