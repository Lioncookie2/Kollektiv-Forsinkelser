from flask import Flask
from app.extensions import db
from app.scheduler import start_scheduler
import os

app = Flask(__name__, 
    static_folder='../static',
    template_folder='../templates'
)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)

# Create database tables
with app.app_context():
    db.create_all()

# Start scheduler
scheduler = start_scheduler()

# Import routes after app is created
from app import routes 