import requests
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test ett enkelt datasett
url = 'https://api.entur.io/realtime/v1/rest/et'
headers = {'ET-Client-Name': 'lasse-forsinkelse-app'}
params = {'datasetId': 'BNR'}  # Test Bane NOR

response = requests.get(url, headers=headers, params=params)
if response.status_code == 200:
    # Lagre responsen
    with open('test_response.xml', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    # Parse XML
    root = ET.fromstring(response.text)
    ns = {'siri': 'http://www.siri.org.uk/siri'}
    
    # Finn alle aktiviteter
    activities = root.findall('.//siri:EstimatedVehicleJourney', ns)
    print(f"Fant {len(activities)} aktiviteter")
    
    if activities:
        # Skriv ut første aktivitet
        first = activities[0]
        print("\nFørste aktivitet:")
        for elem in first.iter():
            if elem.text and elem.text.strip():
                print(f"{elem.tag.split('}')[-1]}: {elem.text}") 