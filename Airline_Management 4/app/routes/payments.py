from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from app.services import payment_service
from app.schemas import PaymentInitiateSchema
from app.utils.responses import success_response, error_response
from app.utils.constants import PAYMENT_FAILED, BOOKING_NOT_FOUND, UNAUTHORIZED, INVALID_INPUT
from app.utils.decorators import passenger_required
from app.exceptions import PaymentError, BookingNotFoundError
from app.models.payment import Payment
from app.models.booking import Booking
from app.models.passenger import Passenger
from app.extensions import db

payments_bp = Blueprint('payments_bp', __name__, url_prefix='/api/v1/payments')

@payments_bp.route('/initiate', methods=['POST'])
@passenger_required()
def initiate():
    try:
        data = PaymentInitiateSchema().load(request.get_json())
        payment = payment_service.PaymentService().initiate_payment(data['booking_id'], data['payment_method'])
        
        result = {
            "payment_id": payment.id,
            "transaction_id": payment.transaction_id,
            "amount": float(payment.amount),
            "payment_method": payment.payment_method.value,
            "payment_status": payment.payment_status.value
        }
        return success_response("Payment initiated", data=result)
        
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except BookingNotFoundError:
        return error_response("Booking not found", BOOKING_NOT_FOUND, status_code=404)
    except PaymentError as e:
        return error_response(str(e), PAYMENT_FAILED, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@payments_bp.route('/confirm', methods=['POST'])
@passenger_required()
def confirm():
    try:
        body = request.get_json()
        transaction_id = body.get('transaction_id')
        gateway_response = body.get('gateway_response')
        
        if not transaction_id or not gateway_response:
            return error_response("transaction_id and gateway_response are required", INVALID_INPUT, status_code=400)
            
        payment = payment_service.PaymentService().confirm_payment(transaction_id, gateway_response)
        
        result = {
            "payment_id": payment.id,
            "transaction_id": payment.transaction_id,
            "payment_status": payment.payment_status.value,
            "booking_status": payment.booking.status.value
        }
        return success_response("Payment confirmed", data=result)
        
    except PaymentError as e:
        return error_response(str(e), PAYMENT_FAILED, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@payments_bp.route('/<int:id>', methods=['GET'])
@passenger_required()
def get_payment(id):
    try:
        user_id = get_jwt_identity()
        payment = Payment.query.get(id)
        
        if not payment or str(payment.booking.passenger.user_id) != str(user_id):
            return error_response("Not authorized or payment not found", UNAUTHORIZED, status_code=403)
            
        result = {
            "payment_id": payment.id,
            "transaction_id": payment.transaction_id,
            "amount": float(payment.amount),
            "payment_method": payment.payment_method.value,
            "payment_status": payment.payment_status.value,
            "payment_date": payment.payment_date.isoformat() if payment.payment_date else None,
            "refund_amount": float(payment.refund_amount) if payment.refund_amount else None,
            "refund_date": payment.refund_date.isoformat() if payment.refund_date else None,
            "gateway_response": payment.gateway_response
        }
        return success_response("Payment retrieved", data=result)
        
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@payments_bp.route('/<int:id>/refund', methods=['POST'])
@passenger_required()
def refund(id):
    try:
        user_id = get_jwt_identity()
        payment = Payment.query.get(id)
        
        if not payment or str(payment.booking.passenger.user_id) != str(user_id):
            return error_response("Not authorized or payment not found", UNAUTHORIZED, status_code=403)
            
        refunded_payment = payment_service.PaymentService().process_refund(id)
        
        result = {
            "refund_amount": float(refunded_payment.refund_amount),
            "refund_date": refunded_payment.refund_date.isoformat(),
            "payment_status": refunded_payment.payment_status.value
        }
        return success_response("Refund processed", data=result)
        
    except PaymentError as e:
        return error_response(str(e), PAYMENT_FAILED, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
