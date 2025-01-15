from datetime import datetime
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnturClient:
    def __init__(self, client_id=None):
        self.client_id = client_id or "kollektiv-forsinkelser"
        self.url = "https://api.entur.io/realtime/v1/rest/et"
        self.headers = {
            "ET-Client-Name": self.client_id,
            "Accept": "application/json"
        }

    def get_realtime_data(self):
        """Get realtime data from Entur API"""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching delays: {e}")
            return None

    # Alias for compatibility
    get_delays = get_realtime_data

entur_client = EnturClient()