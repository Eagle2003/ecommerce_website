from flask import Flask
from hashlib import sha224
from flask_mysql_connector import MySQL
from mysql.connector.errors import IntegrityError
import sys
import json




class baseTableManager() :
    
    app = Flask(__name__)
    mysql = MySQL(app).connection
    COLUMNS = {}
    NAME = None

    
    def Field(column_name:str, data_type:str, primary_key=False, validator=None, loader=None) :
        self.COLUMNS[column_name] = {
            name : column_name,
            data_type : data_type,
            primary_key : primary_key,
            validator : validator,
            loader : loader
        }

class query() :

    q_str = ""    
    TABLE_NAME = None
    TABLE = None

    def __init__ (table : baseTableManager) :
        self.TABLE = table 
    
    def get(*columns) :
        self.q = "SELECT " + " ,",join(columns) + " FROM " + self.TABLE.NAME 
    
    def filter(column, value=None, values=None) :
        self.FITERS = []
        
    
    def addFilter(conjunction:str, column:str, comparison:str, value:str) : 

        





