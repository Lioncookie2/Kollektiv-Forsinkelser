from apscheduler.schedulers.background import BackgroundScheduler
from app.entur_client import update_delays
from flask import current_app

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_delays,
        'interval',
        minutes=1,
        max_instances=1
    )
    scheduler.start()
    return scheduler 