import enum
from app.extensions import db

class PaymentMethodEnum(enum.Enum):
    upi = 'upi'
    credit_card = 'credit_card'
    debit_card = 'debit_card'
    net_banking = 'net_banking'
    cash = 'cash'

class PaymentStatusEnum(enum.Enum):
    initiated = 'initiated'
    success = 'success'
    failed = 'failed'
    refunded = 'refunded'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), unique=True, nullable=False)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethodEnum), nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatusEnum), default=PaymentStatusEnum.initiated, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    refund_amount = db.Column(db.Numeric(10, 2), nullable=True)
    refund_date = db.Column(db.DateTime, nullable=True)
    gateway_response = db.Column(db.JSON, nullable=True)
