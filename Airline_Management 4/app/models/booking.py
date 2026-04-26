import enum
from datetime import datetime, timezone
from app.extensions import db

class BookingStatusEnum(enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    cancelled = 'cancelled'
    completed = 'completed'

class BookingClassEnum(enum.Enum):
    economy = 'economy'
    business = 'business'
    first = 'first'

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(7), unique=True, nullable=False)
    passenger_id = db.Column(db.Integer, db.ForeignKey('passengers.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_class = db.Column(db.Enum(BookingClassEnum), nullable=False)
    status = db.Column(db.Enum(BookingStatusEnum), default=BookingStatusEnum.pending, nullable=False)
    booking_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    cancellation_reason = db.Column(db.Text, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    payment = db.relationship('Payment', backref='booking', uselist=False)
