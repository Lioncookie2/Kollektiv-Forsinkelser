from datetime import datetime
import requests
import logging
from app.extensions import db
from app.models import Delay

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnturClient:
    def __init__(self, client_id=None):
        self.client_id = client_id or "kollektiv-forsinkelser"
        self.url = "https://api.entur.io/realtime/v1/rest/et"
        self.headers = {"ET-Client-Name": self.client_id}

    def get_delays(self):
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching delays: {e}")
            return None

def update_delays():
    """Update delays in the database"""
    try:
        client = EnturClient()
        data = client.get_delays()
        
        if not data:
            return
        
        # Clear old delays
        Delay.query.delete()
        
        # Add new delays
        for activity in data.get('activities', []):
            delay = activity.get('delay', 0)
            if delay > 0:
                line = activity.get('monitoredVehicleJourney', {}).get('lineRef', '')
                station = activity.get('monitoredVehicleJourney', {}).get('monitoredCall', {}).get('stopPointName', '')
                transport_type = activity.get('monitoredVehicleJourney', {}).get('vehicleMode', '').lower()
                
                new_delay = Delay(
                    line=line,
                    delay_minutes=delay,
                    station=station,
                    transport_type=transport_type,
                    timestamp=datetime.now()
                )
                db.session.add(new_delay)
                logger.info(f"La til {line}: {delay} min forsinkelse ved {station}")
        
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error in update_delays: {e}")
        db.session.rollback()