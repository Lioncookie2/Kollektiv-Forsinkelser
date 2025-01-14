import threading
import time
from app.extensions import db, entur_client

class DataCollector:
    def __init__(self, interval):
        self.interval = interval
        self.thread = None
        self.running = False

    def start(self):
        if self.thread is not None:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def _run(self):
        while self.running:
            try:
                self._collect_data()
            except Exception as e:
                print(f"Feil ved datainnhenting: {e}")
            time.sleep(self.interval)

    def _collect_data(self):
        trains = entur_client.get_realtime_data()
        
        for train in trains:
            try:
                db.save_delay(
                    train['line'],
                    train['station'],
                    train['scheduled_time'],
                    train['expected_time']
                )
            except Exception as e:
                print(f"Feil ved lagring av togdata: {e}") 