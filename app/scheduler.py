from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks import update_delays
from flask import current_app

def start_scheduler(app):
    scheduler = BackgroundScheduler()
    
    def scheduled_task():
        with app.app_context():
            update_delays()
    
    scheduler.add_job(
        scheduled_task,
        'interval',
        minutes=1,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=None
    )
    scheduler.start()
    return scheduler 