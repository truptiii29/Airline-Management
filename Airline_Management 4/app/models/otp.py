import enum
from datetime import datetime, timezone
from app.extensions import db

class OTPPurposeEnum(enum.Enum):
    email_verify = 'email_verify'
    password_reset = 'password_reset'
    login_2fa = 'login_2fa'

class OTP(db.Model):
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.Enum(OTPPurposeEnum), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref=db.backref('otps', lazy=True))
