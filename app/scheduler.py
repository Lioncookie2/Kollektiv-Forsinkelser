<<<<<<< HEAD
from app import db, app
from app.models import Delay
from app.entur_client import EnturClient
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def start_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
=======
from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks import update_delays
from flask import current_app

def start_scheduler(app):
>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
    scheduler = BackgroundScheduler()
    
    def scheduled_task():
        with app.app_context():
<<<<<<< HEAD
            try:
                client = EnturClient()
                vehicles = client.get_realtime_data()
                
                if not vehicles:
                    return
                
                # Lagre til database
                new_delays = 0
                for vehicle in vehicles:
                    try:
                        # Sjekk om journey_reference allerede eksisterer
                        existing = Delay.query.filter_by(
                            journey_reference=vehicle['journey_ref']
                        ).first()
                        
                        if existing:
                            continue
                            
                        delay = Delay(
                            timestamp=datetime.now(),
                            line=vehicle['line'],
                            station=vehicle['station'],
                            delay_minutes=vehicle['delay_minutes'],
                            transport_type=vehicle['transport_type'],
                            journey_reference=vehicle['journey_ref']
                        )
                        db.session.add(delay)
                        db.session.commit()
                        new_delays += 1
                        
                    except IntegrityError:
                        db.session.rollback()
                        continue
                    except Exception as e:
                        db.session.rollback()
                        continue
                
            except Exception as e:
                db.session.rollback()
    
    # Kjør hvert 30. sekund
    scheduler.add_job(
        scheduled_task,
        'interval',
        seconds=30,
        id='check_delays'
    )
    
=======
            update_delays()
    
    scheduler.add_job(
        scheduled_task,
        'interval',
        minutes=1,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=None
    )
>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
    scheduler.start()
    return scheduler 