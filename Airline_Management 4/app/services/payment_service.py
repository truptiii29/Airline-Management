import uuid
from datetime import datetime, timezone
from app.extensions import db
from app.models.booking import Booking, BookingStatusEnum
from app.models.payment import Payment, PaymentMethodEnum, PaymentStatusEnum
from app.exceptions import BookingNotFoundError, PaymentError
from app.services.seat_service import SeatService
from app.tasks.email_tasks import send_booking_confirmation_task

class PaymentService:
    def initiate_payment(self, booking_id, payment_method):
        booking = Booking.query.get(booking_id)
        if not booking:
            raise BookingNotFoundError("Booking not found")
            
        if booking.status != BookingStatusEnum.pending:
            raise PaymentError("Booking is not in pending state")
            
        transaction_id = "TXN" + uuid.uuid4().hex[:12].upper()
        
        if isinstance(payment_method, str):
            pm = getattr(PaymentMethodEnum, payment_method)
        else:
            pm = payment_method
            
        payment = Payment(
            booking_id=booking_id,
            transaction_id=transaction_id,
            amount=booking.total_amount,
            payment_method=pm,
            payment_status=PaymentStatusEnum.initiated,
            payment_date=datetime.now(timezone.utc)
        )
        db.session.add(payment)
        db.session.commit()
        
        return payment

    def confirm_payment(self, transaction_id, gateway_response):
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            raise PaymentError("Payment not found")
            
        booking = payment.booking
        
        if gateway_response.get("status") == "success":
            payment.payment_status = PaymentStatusEnum.success
            payment.payment_date = datetime.now(timezone.utc)
            booking.status = BookingStatusEnum.confirmed
            
            SeatService().confirm_seat(
                flight_id=booking.flight_id,
                seat_number=booking.seat_number,
                user_id=booking.passenger.user_id
            )
            db.session.commit()
            
            send_booking_confirmation_task.delay(booking.id)
        else:
            payment.payment_status = PaymentStatusEnum.failed
            payment.gateway_response = gateway_response
            db.session.commit()
            
        return payment

    def process_refund(self, payment_id):
        payment = Payment.query.get(payment_id)
        if not payment or payment.payment_status != PaymentStatusEnum.success:
            raise PaymentError("Payment not found or not successful")
            
        booking = payment.booking
        flight_departure = booking.flight_details.departure_time
        
        now = datetime.now(timezone.utc)
        if flight_departure.tzinfo is None:
            flight_departure = flight_departure.replace(tzinfo=timezone.utc)
            
        time_diff = flight_departure - now
        hours_until = time_diff.total_seconds() / 3600
        
        if hours_until > 24:
            refund_percentage = 0.8
        else:
            refund_percentage = 0.5
            
        payment.refund_amount = float(payment.amount) * refund_percentage
        payment.payment_status = PaymentStatusEnum.refunded
        payment.refund_date = now
        
        db.session.commit()
        return payment
