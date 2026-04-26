import enum
from datetime import datetime, timezone
from app.extensions import db

class FlightStatusEnum(enum.Enum):
    scheduled = 'scheduled'
    boarding = 'boarding'
    departed = 'departed'
    in_air = 'in_air'
    landed = 'landed'
    delayed = 'delayed'
    cancelled = 'cancelled'

class FlightStatus(db.Model):
    __tablename__ = 'flight_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), unique=True, nullable=False)
    status = db.Column(db.Enum(FlightStatusEnum), default=FlightStatusEnum.scheduled, nullable=False)
    delay_minutes = db.Column(db.Integer, default=0)
    delay_reason = db.Column(db.String(255), nullable=True)
    gate_number = db.Column(db.String(20), nullable=True)
    terminal = db.Column(db.String(20), nullable=True)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    flight = db.relationship('Flight', backref=db.backref('status', uselist=False))
