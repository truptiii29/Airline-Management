from datetime import datetime, timezone
from app.extensions import db

class Passenger(db.Model):
    __tablename__ = 'passengers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    passport_number = db.Column(db.String(50), unique=True, nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('passenger', uselist=False))
    bookings = db.relationship('Booking', backref='passenger', lazy='dynamic')
