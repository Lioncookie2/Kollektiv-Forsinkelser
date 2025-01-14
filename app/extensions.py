from app.database import Database
from app.entur_client import EnturClient
from app.config import Config

db = Database(Config.SQLITE_DB_PATH)
entur_client = EnturClient(Config.ENTUR_CLIENT_ID) 