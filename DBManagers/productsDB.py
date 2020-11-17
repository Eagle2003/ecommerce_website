from flask import Flask
from hashlib import sha224
from flask_mysql_connector import MySQL
from mysql.connector.errors import IntegrityError
import sys
import json

app = Flask(__name__)

mysql = MySQL(app)


def getProductByID (id, columns="*") :
    q = f"SELECT {columns} FROM products WHERE id = %s "
    var = [id]

    #Execute statement
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute(q, var)
    res = cursor.fetchall()
    res = list(map(lambda row : json_loader(row, 'images'), res))
    return res[0]

def getProducts(filter=None, limit=8, columns="*"):
    #Basic Query
    q = f"SELECT {columns}  FROM products "
    var = []
    if filter : q += " WHERE " + filter
    #add the limit to the results
    q += f" LIMIT  {limit} "
            
    #Execute statement
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute(q, var)
    res = cursor.fetchall()
    res = list(map(lambda row : json_loader(row, 'images'), res))
    return res

def searchProducts (keyword, limit=20, offset=0, columns="*"):
    keyword = ".?".join(list(keyword))
    while True : 
        q = f"SELECT {columns} FROM products WHERE name REGEXP %s || item REGEXP %s || subcategory REGEXP %s "
        var = [keyword, keyword, keyword]
        q += f"LIMIT {limit} OFFSET {offset}"
        #Execute statement
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute(q, var)
        res = cursor.fetchall()
        res = list(map(lambda row : json_loader(row, 'images'), res))
        return res

def keywordSearch (keyword):
    keyword= '%' + keyword + '%'
    q="SELECT name FROM products WHERE name LIKE %s UNION SELECT item  FROM products WHERE item LIKE %s LIMIT 10;"
    var = [keyword, keyword]
    #Execute statement
    cursor = mysql.connection.cursor()
    cursor.execute(q, var)
    res = cursor.fetchall()
    res = list(map(lambda row : row[0], res))
    return res    

def getCategories(category=None, subcategory=None)  :

    var = []
    if category :
        q = "SELECT name FROM subcategory WHERE parent = %s "
        var = [category]
    elif subcategory :
        q = "SEELCT name FROM items WHERE parent = %s "
        var = [subcategory]
    
    q += f" LIMIT {limit} "    
    cursor = mysql.connection.cursor()
    cursor.execute(q, var)
    res = cursor.fetchall()
    return res
       

#A fucntion to load Json objects from a dict
def json_loader(row : dict, key : str) :
    row[key]  = json.loads(row[key])
    return row
