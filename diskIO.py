from flask import current_app
import uuid
import os


def saveFormDataToDisk(save_location, data) :
    ext = data.filename.split(".")[-1]
    file_name  = uuid.uuid4().hex +"."+ ext
    path = os.path.join(save_location, file_name)
    data.save(path)
    current_app.logger.info(f"Saved File at path : {path}")
    return file_name



def deleteFromDisk(file_path, file_name):
    try :
        path = os.path.join(file_path, file_name)
        os.remove(path)
        return True
    except Exception as e : 
        current_app.logger.info(f"Error while printi deleting file : {file_path}, {e}" )
        return False
