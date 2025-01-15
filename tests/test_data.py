from app.entur_client import EnturClient
import time

def test_transport_type(transport_type):
    client = EnturClient()
    print(f"\nHenter data for {transport_type}...")
    
    data = client.get_realtime_data(transport_type=transport_type)
    
    if data:
        print(f"\nFant {len(data)} avganger totalt")
        print("\nViser de første 5 avgangene:")
        for vehicle in data[:5]:
            print(f"\nLinje: {vehicle['line']}")
            print(f"Stasjon: {vehicle['station']}")
            print(f"Plattform: {vehicle['platform']}")
            print(f"Status: {vehicle['status']}")
            print(f"Forsinkelse: {vehicle['delay_minutes']} minutter")
            print(f"Operatør: {vehicle['operator']}")
    else:
        print("Ingen data funnet")

def main():
    while True:
        print("\n=== Entur Data Test ===")
        print("1: Test tog (rail)")
        print("2: Test buss (bus)")
        print("3: Test trikk (tram)")
        print("q: Avslutt")
        
        valg = input("\nVelg transporttype (1-3) eller 'q' for å avslutte: ").lower()
        
        if valg == 'q':
            break
        elif valg == '1':
            test_transport_type('rail')
        elif valg == '2':
            test_transport_type('bus')
        elif valg == '3':
            test_transport_type('tram')
        else:
            print("Ugyldig valg. Prøv igjen.")

if __name__ == "__main__":
    main() 