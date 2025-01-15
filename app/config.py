import os

class Config:
    DB_PATH = os.path.join(os.environ.get('RENDER_VOLUME_PATH', ''), 'site.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENTUR_CLIENT_ID = os.getenv('ENTUR_CLIENT_ID', 'kollektiv-forsinkelser') 