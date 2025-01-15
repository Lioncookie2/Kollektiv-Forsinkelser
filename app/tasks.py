from datetime import datetime
from app.extensions import db
from app.models import Delay
from app.entur_client import entur_client
import logging

logger = logging.getLogger(__name__)

def update_delays():
    """Update delays in the database"""
    try:
        data = entur_client.get_delays()
        
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