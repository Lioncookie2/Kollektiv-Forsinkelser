from datetime import datetime
import requests
import logging

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

entur_client = EnturClient()