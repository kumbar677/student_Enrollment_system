import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-CHANGE-IN-PROD'
    # Defaulting to root with empty password for local dev ease, can be overridden
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://root:2003@localhost/enrollment_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'ikumbar59@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'idhy eynv wqvc ypjy'
    MAIL_DEFAULT_SENDER = ('New2', MAIL_USERNAME)
