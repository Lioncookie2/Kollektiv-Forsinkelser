from datetime import datetime
from app.extensions import db
from app.models import Delay
from app.entur_client import entur_client
import logging

logger = logging.getLogger(__name__)

def update_delays():
    """Update delays in the database"""
    try:
        data = entur_client.get_realtime_data()
        
        if not data:
            logger.error("No data received from Entur API")
            return
        
        # Clear old delays
        Delay.query.delete()
        
        # Add new delays
        for activity in data.get('activities', []):
            monitored_vehicle_journey = activity.get('monitoredVehicleJourney', {})
            monitored_call = monitored_vehicle_journey.get('monitoredCall', {})
            
            delay = monitored_call.get('delay', 0)
            if delay > 0:
                line = monitored_vehicle_journey.get('lineRef', '')
                station = monitored_call.get('stopPointName', '')
                transport_type = monitored_vehicle_journey.get('vehicleMode', '').lower()
                
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