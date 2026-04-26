from app.extensions import db

class Airport(db.Model):
    __tablename__ = 'airports'
    
    id = db.Column(db.Integer, primary_key=True)
    iata_code = db.Column(db.String(3), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
