from app.extensions import db

class Flight(db.Model):
    __tablename__ = 'flights'
    
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False)
    source_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    destination_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircraft.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    base_price_economy = db.Column(db.Numeric(10, 2), nullable=False)
    base_price_business = db.Column(db.Numeric(10, 2), nullable=False)
    base_price_first = db.Column(db.Numeric(10, 2), nullable=False)
    available_economy = db.Column(db.Integer, nullable=False)
    available_business = db.Column(db.Integer, nullable=False)
    available_first = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    source_airport = db.relationship('Airport', foreign_keys=[source_airport_id])
    destination_airport = db.relationship('Airport', foreign_keys=[destination_airport_id])
    aircraft = db.relationship('Aircraft')
    
    bookings = db.relationship('Booking', backref='flight_details', lazy='dynamic')
    seat_map = db.relationship('SeatMap', backref='flight_details', lazy='dynamic')
