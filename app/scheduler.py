from app import db, app
from app.models import Delay
from app.entur_client import EnturClient
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def start_scheduler(app):
    from apscheduler.schedulers.background import BackgroundScheduler
    scheduler = BackgroundScheduler()
    
    def scheduled_task():
        with app.app_context():
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
    
    scheduler.start()
    return scheduler 