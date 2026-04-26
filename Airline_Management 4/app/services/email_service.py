import logging
from flask import render_template
from flask_mail import Message
from app.extensions import mail
from app.models.user import User
from app.models.passenger import Passenger
from app.models.booking import Booking
from app.models.otp import OTPPurposeEnum

logger = logging.getLogger(__name__)

def send_otp_email(user_id, otp_code, purpose):
    try:
        user = User.query.get(user_id)
        passenger = Passenger.query.filter_by(user_id=user_id).first()
        passenger_name = f"{passenger.first_name} {passenger.last_name}" if passenger else "User"
        
        subject = "Your OTP Code"
        if purpose == OTPPurposeEnum.email_verify.value or purpose == OTPPurposeEnum.email_verify:
            subject = "Verify Your Email Address"
        elif purpose == OTPPurposeEnum.password_reset.value or purpose == OTPPurposeEnum.password_reset:
            subject = "Password Reset Request"
            
        html_body = render_template(
            "otp_verification.html",
            passenger_name=passenger_name,
            otp_code=otp_code,
            expiry_minutes=10
        )
        
        msg = Message(subject=subject, recipients=[user.email], html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending OTP email: {str(e)}")
        return False

def send_booking_confirmation(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return False
            
        passenger = booking.passenger
        user = passenger.user
        flight = booking.flight_details
        
        html_body = render_template(
            "booking_confirmation.html",
            booking=booking,
            passenger=passenger,
            flight=flight
        )
        
        msg = Message(subject="Booking Confirmation", recipients=[user.email], html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending booking confirmation email: {str(e)}")
        return False

def send_cancellation_email(booking_id):
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return False
            
        passenger = booking.passenger
        user = passenger.user
        payment = booking.payment
        
        refund_amount = None
        if payment and payment.payment_status.value == "refunded":
            refund_amount = payment.refund_amount
            
        html_body = render_template(
            "booking_cancellation.html",
            booking=booking,
            passenger=passenger,
            refund_amount=refund_amount
        )
        
        msg = Message(subject="Booking Cancellation", recipients=[user.email], html=html_body)
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Error sending cancellation email: {str(e)}")
        return False
