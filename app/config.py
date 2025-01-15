import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENTUR_CLIENT_ID = os.getenv('ENTUR_CLIENT_ID', 'kollektiv-forsinkelser') 