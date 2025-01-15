import os
from flask import Flask
<<<<<<< HEAD
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
=======
from app.extensions import db
from app.scheduler import start_scheduler
from app.config import Config
import os

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)

    # Create EnturClient instance
    from app.entur_client import EnturClient
    app.entur_client = EnturClient()

    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register routes
    from app.routes import init_routes
    app = init_routes(app)

    # Start scheduler with app context
    scheduler = start_scheduler(app)
    app.scheduler = scheduler

    return app 
>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
