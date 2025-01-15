from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks import update_delays
from flask import current_app

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_delays,
        'interval',
        minutes=1,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=None
    )
    scheduler.start()
    return scheduler 