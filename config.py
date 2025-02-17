import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sikkerhet
    SECRET_KEY = 'dev'
    
    # Debug modus
    DEBUG = True 