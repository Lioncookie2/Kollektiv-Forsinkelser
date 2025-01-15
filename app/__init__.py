from flask import Flask
from app.extensions import db
from app.scheduler import start_scheduler
from app.config import Config
import os

def create_app():
    app = Flask(__name__, 
        static_url_path='',
        static_folder='../static',
        template_folder='../templates'
    )

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

    # Start scheduler with app context
    scheduler = start_scheduler(app)
    app.scheduler = scheduler

    # Register routes
    from app.routes import init_routes
    init_routes(app)

    return app

app = create_app() 