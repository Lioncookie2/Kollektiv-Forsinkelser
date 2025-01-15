from flask_sqlalchemy import SQLAlchemy
from app.entur_client import EnturClient

db = SQLAlchemy()
entur_client = EnturClient() 