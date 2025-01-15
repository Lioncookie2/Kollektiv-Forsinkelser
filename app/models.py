from app import db
from datetime import datetime

class Delay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
<<<<<<< HEAD
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
=======
>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
    line = db.Column(db.String(50), nullable=False)
    station = db.Column(db.String(100), nullable=False)
    delay_minutes = db.Column(db.Integer, nullable=False)
    transport_type = db.Column(db.String(20), nullable=False)
<<<<<<< HEAD
    journey_reference = db.Column(db.String(100), unique=True)
    
=======
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
    def __repr__(self):
        return f'<Delay {self.line} at {self.station}: {self.delay_minutes} min>'

class DailySummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transport_type = db.Column(db.String(20), nullable=False)
    total_delays = db.Column(db.Integer, default=0)
    total_trips = db.Column(db.Integer, default=0)
    avg_delay = db.Column(db.Float, default=0.0)
    max_delay = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('date', 'transport_type'),) 