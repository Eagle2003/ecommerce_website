from flask import Flask, current_app
from hashlib import sha224
from flask_mysql_connector import MySQL
from mysql.connector.errors import IntegrityError
from secrets import token_urlsafe
from datetime import datetime, timedelta
import sys



mysql = MySQL(current_app)


    

# To register a user 
def addUser(email : str,  password : str) : 
    q = "insert into users (email,  password) values (%s,  sha2(%s, 224));"
    try : 
        cur = mysql.connection.cursor()
        cur.execute(q, (email,  password))
        mysql.connection.commit()
        cur.close()
    except IntegrityError :  
        mysql.connection.rollback()
        return False

    return True

# Get user data given email
def getUser(email : str ) :
    q = "SELECT * FROM users WHERE email = %s"
    var = [email]
    cur = mysql.connection.cursor(dictionary=True)
    cur.execute(q, var)
    res = cur.fetchone()
    cur.close()
    return res

# Genrates an Acitvation Code activate user
def getActivationCode(email : str) : 
    token = token_urlsafe(32)
    q = "INSERT INTO activation  (activation_code, email) VALUES (%s, %s)"
    var = [token, email]
    try : 
        cur = mysql.connection.cursor()
        cur.execute(q, var)
        mysql.connection.commit()
    except IntegrityError as e :
        mysql.connection.rollback()
        print("Duplicate token genrated that is rare trying again !")
        return getActivationCode(email)
    
    except Exception as e :
        mysql.connection.rollback()
        print("Error accured while adding token attempting again !" , e)
    
    return token

# Activates User based on the token 
def activateUser(token : str) : 
    q = "SELECT email FROM activation WHERE activation_code = %s"
    var = [token]
    cur = mysql.connection.cursor()
    cur.execute(q, var)
    res = cur.fetchone()
    if res : 
        try : 
            q = "UPDATE  users SET activated = true WHERE email = %s"
            var = [res[0]]
            cur.execute(q, var)
            q = "DELETE FROM activation WHERE activation_code = %s"
            var = [token]
            cur.execute(q, var)
            mysql.connection.commit()
            cur.close()
            return True
        except Exception as e: 
            print("Error occured while activating account ", e)
            mysql.connection.rollback()
        
    return False




        





    
