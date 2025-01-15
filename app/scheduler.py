from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks import update_delays

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