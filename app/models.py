from app import db
from datetime import datetime

class Delay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    line = db.Column(db.String(20), nullable=False)
    line_name = db.Column(db.String(100))
    transport_type = db.Column(db.String(20), nullable=False)
    delay_minutes = db.Column(db.Integer, nullable=False)
    station = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    journey_reference = db.Column(db.String(100), unique=True)  # Unikt ID for hver reise
    
    def __repr__(self):
        return f'<Delay {self.line} {self.delay_minutes}min>'

class DailySummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transport_type = db.Column(db.String(20), nullable=False)
    total_delays = db.Column(db.Integer, default=0)
    total_trips = db.Column(db.Integer, default=0)
    avg_delay = db.Column(db.Float, default=0.0)
    max_delay = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('date', 'transport_type'),) 