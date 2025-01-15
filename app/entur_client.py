import requests
import xml.etree.ElementTree as ET
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EnturClient:
    def __init__(self, client_id=None):
        self.client_id = client_id or "kollektiv-forsinkelser"
        self.base_url = "https://api.entur.io/realtime/v1/rest/vm"
        self.headers = {
            'ET-Client-Name': 'togtrafikk-monitor',
            'Accept': 'application/xml'
        }
        self.ns = {
            'ns': 'http://www.siri.org.uk/siri'
        }

    def get_realtime_data(self, transport_type=None):
        """Henter sanntidsdata for spesifisert transporttype"""
        try:
            logger.info("Starter datahenting fra Entur API...")
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                root = ET.fromstring(response.text)
                vehicles = self._parse_vehicles(root, transport_type)
                logger.info(f"Totalt hentet {len(vehicles)} kjøretøy")
                return vehicles
            else:
                logger.error(f"Feil fra API: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Kritisk feil i datahenting: {str(e)}")
            return []

    def _parse_vehicles(self, root, transport_type=None):
        vehicles = []
        try:
            activities = root.findall('.//ns:VehicleActivity', self.ns)
            logger.info(f"Fant {len(activities)} aktiviteter å parse")
            
            for activity in activities:
                try:
                    journey = activity.find('.//ns:MonitoredVehicleJourney', self.ns)
                    if journey is None:
                        continue
                    
                    # Finn journey reference
                    frame_ref = journey.find('.//ns:FramedVehicleJourneyRef/ns:DatedVehicleJourneyRef', self.ns)
                    if frame_ref is None:
                        continue
                    journey_ref = frame_ref.text
                    
                    # Hent linjenummer og navn
                    line_ref = journey.find('.//ns:LineRef', self.ns)
                    published_line = journey.find('.//ns:PublishedLineName', self.ns)
                    destination = journey.find('.//ns:DestinationName', self.ns)
                    
                    if line_ref is None:
                        continue
                        
                    line = line_ref.text.split(':')[-1]
                    line_name = published_line.text if published_line is not None else line
                    destination_text = destination.text if destination is not None else "Ukjent destinasjon"
                    
                    # Bestem transporttype mer presist
                    transport_type = 'bus'  # Standard er buss
                    if 'BNR' in line_ref.text:
                        transport_type = 'rail'
                    elif 'RUT:Tram' in line_ref.text or any(str(x) in line_name for x in [11, 12, 13, 17, 18, 19]):
                        transport_type = 'tram'
                    
                    # Hent forsinkelse
                    delay = journey.find('.//ns:Delay', self.ns)
                    if delay is not None:
                        delay_text = delay.text
                        if delay_text.startswith('PT'):
                            minutes = 0
                            if 'M' in delay_text:
                                minutes = int(delay_text.split('M')[0].replace('PT', ''))
                            
                            if minutes > 0:
                                # Hent stasjonsnavn
                                stop = journey.find('.//ns:StopPointName', self.ns)
                                station = stop.text if stop is not None else "Ukjent stasjon"
                                
                                vehicle_data = {
                                    'journey_ref': journey_ref,
                                    'line': line,
                                    'line_name': f"{line_name} mot {destination_text}",
                                    'delay_minutes': minutes,
                                    'transport_type': transport_type,
                                    'station': station
                                }
                                vehicles.append(vehicle_data)
                                logger.info(f"La til {line}: {minutes} min forsinkelse ved {station}")
                            
                except Exception as e:
                    logger.error(f"Feil ved parsing av kjøretøy: {str(e)}")
                    continue
                    
            return vehicles
            
        except Exception as e:
            logger.error(f"Feil ved parsing av data: {e}")
            return []

    def _parse_datetime(self, dt_str: str) -> datetime:
        """Konverterer ISO datetime string til datetime objekt"""
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

    def _get_dataset_for_transport(self, transport_type):
        """Velger riktig datasett basert på transporttype"""
        if transport_type == 'rail':
            return {'id': 'BNR', 'name': 'Bane NOR'}
        elif transport_type in ['bus', 'tram']:
            return {'id': 'RUT', 'name': 'Ruter'}
        else:
            return {'id': None, 'name': 'Alle'}

client = EnturClient()
data = client.get_realtime_data(transport_type='bus')  # Endre til ønsket transporttype, f.eks. 'train'
print(data)
print(data)