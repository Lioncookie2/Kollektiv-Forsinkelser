from apscheduler.schedulers.background import BackgroundScheduler
from app.entur_client import update_delays

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_delays, 'interval', minutes=1)
    scheduler.start()
    return scheduler 