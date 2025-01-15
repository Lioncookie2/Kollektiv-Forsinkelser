import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
import logging

# Initialize Flask app
app = Flask(__name__,
    static_folder='../static',
    template_folder='../templates'
)

# Set up logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Database config
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import routes after app is created
from app.routes import init_routes
init_routes(app)

# Create database tables
with app.app_context():
    db.create_all()
    app.logger.info('Database tables created successfully')

# Start the scheduler
from app.scheduler import start_scheduler
scheduler = start_scheduler(app) 