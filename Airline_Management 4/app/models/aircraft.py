import enum
from app.extensions import db

class SeatClassEnum(enum.Enum):
    economy = 'economy'
    business = 'business'
    first = 'first'

class Aircraft(db.Model):
    __tablename__ = 'aircraft'
    
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    economy_seats = db.Column(db.Integer, nullable=False)
    business_seats = db.Column(db.Integer, nullable=False)
    first_class_seats = db.Column(db.Integer, nullable=False)
    seat_layout = db.Column(db.JSON, nullable=False)

class SeatMap(db.Model):
    __tablename__ = 'seat_maps'
    
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_class = db.Column(db.Enum(SeatClassEnum), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    is_window = db.Column(db.Boolean, default=False)
    is_aisle = db.Column(db.Boolean, default=False)
    is_emergency_exit = db.Column(db.Boolean, default=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    locked_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('flight_id', 'seat_number', name='uix_flight_seat'),
    )
