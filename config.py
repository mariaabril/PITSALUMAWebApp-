import os

# GCP
CLOUDSQL_USER = 'root'
CLOUDSQL_PASSWORD = 'meruchy'
CLOUDSQL_DATABASE = 'pitsaluma'
CLOUDSQL_CONNECTION_NAME = 'testpitsalumawebapp:europe-west3:pitsaluma-db'
LOCAL_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{nam}:{pas}@127.0.0.1:3306/{dbn}').format (
    nam=CLOUDSQL_USER,
    pas=CLOUDSQL_PASSWORD,
    dbn=CLOUDSQL_DATABASE,
)

LIVE_SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://{nam}:{pas}@localhost/{dbn}?unix_socket=/cloudsql/{con}').format (
    nam=CLOUDSQL_USER,
    pas=CLOUDSQL_PASSWORD,
    dbn=CLOUDSQL_DATABASE,
    con=CLOUDSQL_CONNECTION_NAME,
)

class Config(object):
    SECRET_KEY = 'my_secret_key'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'pitsaluma@gmail.com'
    MAIL_PASSWORD = os.environ.get('PASSWORD_EMAIL_CF')
    if os.environ.get ('GAE_INSTANCE'):
        SQLALCHEMY_DATABASE_URI = LIVE_SQLALCHEMY_DATABASE_URI
    else:
        SQLALCHEMY_DATABASE_URI = LOCAL_SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pitsaluma.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MULTITHREADING = True
    
class DevelopmentConfig(Config):
    DEBUG = True
    MULTITHREADING = True
    SEND_FILE_MAX_AGE_DEFAULT = 0