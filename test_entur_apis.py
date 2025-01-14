import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time

def test_api(url, params=None, transport_type="", description=""):
    headers = {
        'ET-Client-Name': 'lasse-forsinkelse-app'
    }
    
    print(f"\nTester {description}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            ns = {'siri': 'http://www.siri.org.uk/siri'}
            
            # Finn alle kjøretøy
            vehicles = root.findall('.//siri:EstimatedVehicleJourney', ns)
            
            # Filter basert på transporttype hvis spesifisert
            if transport_type:
                vehicles = [v for v in vehicles 
                          if v.find('.//siri:VehicleMode', ns).text.lower() == transport_type.lower()]
            
            print(f"Fant {len(vehicles)} {transport_type if transport_type else 'totalt'}")
            
            # Vis detaljer for første 3 kjøretøy
            for vehicle in vehicles[:3]:
                line = vehicle.find('.//siri:PublishedLineName', ns).text
                mode = vehicle.find('.//siri:VehicleMode', ns).text
                delay = vehicle.find('.//siri:Delay', ns)
                delay_text = delay.text if delay is not None else "Ingen forsinkelse"
                
                print(f"\nLinje: {line}")
                print(f"Type: {mode}")
                print(f"Forsinkelse: {delay_text}")
            
    except Exception as e:
        print(f"Feil: {e}")
    
    print("-" * 80)

def main():
    base_url = "https://api.entur.io/realtime/v1/rest/et"
    
    # Test alle transportmidler
    test_api(
        base_url,
        None,
        "",
        "Alle transportmidler"
    )
    
    # Test bare tog
    test_api(
        base_url,
        None,
        "rail",
        "Bare tog"
    )
    
    # Test bare buss
    test_api(
        base_url,
        None,
        "bus",
        "Bare buss"
    )
    
    # Test spesifikt VY tog
    test_api(
        base_url,
        {"datasetId": "NSB"},
        "rail",
        "VY tog"
    )

if __name__ == "__main__":
    main() 