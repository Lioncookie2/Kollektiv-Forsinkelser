from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os

# Initialiser Flask med custom template og static folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
app = Flask(__name__, 
    static_folder='../static',
    template_folder='../templates'
)

# Database konfigurasjon
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser database
db = SQLAlchemy(app)

# Enkel logging til konsoll
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialiser Entur client
from app.entur_client import EnturClient
entur_client = EnturClient()

from app import routes, models

# Opprett databasetabeller
with app.app_context():
    db.create_all() 