from flask import Flask
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