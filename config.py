import os

class Config (object) :
    # Falsk Configs
    SECRET_KEY = "Not_an_AmazonN_CopY"
    TEMPLATES_AUTO_RELOAD = True
    BASE_URL = "http://readmythoughts.ddns.net:5000/"
    MAX_CONTENT_LENGTHs = 4 * 1024 * 1024 #4mb max file size

    # MySQL CONfigurations
    MYSQL_USER = 'root'
    MYSQL_DATABASE = 'nancy'
    MYSQL_PASSWORD = 'tony2003'
    MYSQL_DATABASE	= 'nancy'
    
    # Falsk-mail Configs 
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = 'romeyp20@gmail.com'
    MAIL_PASSWORD = 'cuckoo'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # Path Configs
    UPLOAD_FOLDER = "D:\\Board Project -2\\nancy\\media"
    THUMBNAILS_FOLDER = os.path.join(UPLOAD_FOLDER, "shop\\thumbnails")
    SELLER_PROFILE_FOLDER = os.path.join(UPLOAD_FOLDER, "seller\\profile_pictures")
    SELLER_COVER_FOLDER = os.path.join(UPLOAD_FOLDER, "seller\\store_cover")
    USER_PROFILE_FOLDER = os.path.join(UPLOAD_FOLDER, "user\\profile_pictures")
    BANNERS_FOLDER = os.path.join(UPLOAD_FOLDER, "shop\\banners")