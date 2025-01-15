import requests
import xml.etree.ElementTree as ET
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_train_data():
    """Test-funksjon for å hente togdata fra Entur API"""
    base_url = "https://api.entur.io/realtime/v1/rest/vm"
    headers = {
        'ET-Client-Name': 'test-train-monitor',
        'Accept': 'application/xml'
    }
    
    # Liste over kjente tog-operatører og prefixer
    train_operators = {
        'VY': 'Vy',
        'VYG': 'Vy Gjøvikbanen',
        'FLY': 'Flytoget',
        'SJ': 'SJ Nord',
        'GO': 'Go-Ahead Nordic'
    }
    
    try:
        logger.info("Henter data fra Entur API...")
        response = requests.get(base_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            ns = {'ns': 'http://www.siri.org.uk/siri'}
            
            activities = root.findall('.//ns:VehicleActivity', ns)
            logger.info(f"Fant totalt {len(activities)} aktiviteter")
            
            trains_found = 0
            
            for activity in activities:
                try:
                    journey = activity.find('.//ns:MonitoredVehicleJourney', ns)
                    if journey is not None:
                        line_ref = journey.find('.//ns:LineRef', ns)
                        vehicle_mode = journey.find('.//ns:VehicleMode', ns)
                        operator = journey.find('.//ns:OperatorRef', ns)
                        
                        # Sjekk om dette faktisk er et tog
                        is_train = False
                        if vehicle_mode is not None and vehicle_mode.text.lower() == 'rail':
                            is_train = True
                        elif line_ref is not None:
                            operator_prefix = line_ref.text.split(':')[0] if ':' in line_ref.text else ''
                            if operator_prefix in train_operators:
                                is_train = True
                        
                        if is_train:
                            trains_found += 1
                            logger.info("\nTog funnet:")
                            logger.info(f"Operatør: {train_operators.get(operator_prefix, 'Ukjent')}")
                            
                            line_name = journey.find('.//ns:PublishedLineName', ns)
                            origin = journey.find('.//ns:OriginName', ns)
                            destination = journey.find('.//ns:DestinationName', ns)
                            delay = journey.find('.//ns:Delay', ns)
                            location = journey.find('.//ns:VehicleLocation', ns)
                            
                            logger.info(f"Linje: {line_name.text if line_name is not None else 'Ukjent'}")
                            logger.info(f"Fra: {origin.text if origin is not None else 'Ukjent'}")
                            logger.info(f"Til: {destination.text if destination is not None else 'Ukjent'}")
                            logger.info(f"Forsinkelse: {delay.text if delay is not None else 'Ingen'}")
                            
                            if location is not None:
                                lat = location.find('.//ns:Latitude', ns)
                                lon = location.find('.//ns:Longitude', ns)
                                if lat is not None and lon is not None:
                                    logger.info(f"Posisjon: {lat.text}, {lon.text}")
                            
                            logger.info("-" * 50)
                            
                except Exception as e:
                    logger.error(f"Feil ved parsing av aktivitet: {str(e)}")
                    continue
            
            logger.info(f"\nFant totalt {trains_found} tog i sanntidssystemet")
                
        else:
            logger.error(f"Feil fra API: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Kritisk feil: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    get_train_data() 