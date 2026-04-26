from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity, get_jwt
from app.services import booking_service
from app.schemas import BookingCreateSchema
from app.utils.responses import success_response, error_response
from app.utils.constants import UNAUTHORIZED, SEAT_LOCKED, BOOKING_NOT_FOUND, INVALID_INPUT
from app.utils.decorators import passenger_required
from app.exceptions import BookingNotFoundError, SeatLockConflictError
from app.models.passenger import Passenger
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.flight import Flight
from app.models.airport import Airport
from app.extensions import db

bookings_bp = Blueprint('bookings_bp', __name__, url_prefix='/api/v1/bookings')

@bookings_bp.route('/', methods=['POST'])
@passenger_required()
def create():
    try:
        user_id = get_jwt_identity()
        passenger = Passenger.query.filter_by(user_id=user_id).first()
        if not passenger:
            return error_response("Passenger profile not found", UNAUTHORIZED, status_code=401)
            
        data = BookingCreateSchema().load(request.get_json())
        
        booking = booking_service.create_booking(
            passenger_id=passenger.id,
            flight_id=data['flight_id'],
            seat_number=data['seat_number'],
            seat_class=data['seat_class'],
            user_id=user_id
        )
        
        result = {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "passenger_id": booking.passenger_id,
            "flight_id": booking.flight_id,
            "seat_number": booking.seat_number,
            "seat_class": booking.seat_class.value,
            "status": booking.status.value,
            "booking_date": booking.booking_date.isoformat(),
            "total_amount": float(booking.total_amount)
        }
        return success_response("Booking created", data=result, status_code=201)
        
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except SeatLockConflictError as e:
        return error_response(str(e), SEAT_LOCKED, status_code=409)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@bookings_bp.route('/', methods=['GET'])
@passenger_required()
def list_bookings():
    try:
        user_id = get_jwt_identity()
        passenger = Passenger.query.filter_by(user_id=user_id).first()
        if not passenger:
            return error_response("Passenger profile not found", UNAUTHORIZED, status_code=401)
            
        bookings = Booking.query.filter_by(passenger_id=passenger.id).order_by(Booking.booking_date.desc()).all()
        
        results = []
        for b in bookings:
            flight = b.flight_details
            info = {
                "booking_id": b.id,
                "booking_reference": b.booking_reference,
                "seat_number": b.seat_number,
                "seat_class": b.seat_class.value,
                "status": b.status.value,
                "booking_date": b.booking_date.isoformat(),
                "total_amount": float(b.total_amount),
                "flight": {
                    "flight_number": flight.flight_number,
                    "source_iata": flight.source_airport.iata_code,
                    "destination_iata": flight.destination_airport.iata_code,
                    "departure_time": flight.departure_time.isoformat()
                }
            }
            if b.payment:
                info["payment"] = {
                    "payment_status": b.payment.payment_status.value,
                    "amount": float(b.payment.amount)
                }
            results.append(info)
            
        return success_response("Bookings retrieved", data=results)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@bookings_bp.route('/<int:id>', methods=['GET'])
@passenger_required()
def get_booking(id):
    try:
        user_id = get_jwt_identity()
        passenger = Passenger.query.filter_by(user_id=user_id).first()
        
        booking = Booking.query.filter_by(id=id, passenger_id=passenger.id).first()
        if not booking:
            raise BookingNotFoundError("Booking not found")
            
        flight = booking.flight_details
        result = {
            "booking_id": booking.id,
            "booking_reference": booking.booking_reference,
            "seat_number": booking.seat_number,
            "seat_class": booking.seat_class.value,
            "status": booking.status.value,
            "booking_date": booking.booking_date.isoformat(),
            "total_amount": float(booking.total_amount),
            "flight": {
                "flight_number": flight.flight_number,
                "source_iata": flight.source_airport.iata_code,
                "destination_iata": flight.destination_airport.iata_code,
                "departure_time": flight.departure_time.isoformat(),
                "arrival_time": flight.arrival_time.isoformat()
            }
        }
        if booking.payment:
            result["payment"] = {
                "payment_status": booking.payment.payment_status.value,
                "amount": float(booking.payment.amount),
                "transaction_id": booking.payment.transaction_id
            }
            
        return success_response("Booking retrieved", data=result)
    except BookingNotFoundError:
        return error_response("Booking not found", BOOKING_NOT_FOUND, status_code=404)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@bookings_bp.route('/<int:id>/cancel', methods=['PUT'])
@passenger_required()
def cancel(id):
    try:
        user_id = get_jwt_identity()
        passenger = Passenger.query.filter_by(user_id=user_id).first()
        
        reason = request.get_json().get("cancellation_reason") if request.get_json() else None
        
        booking = booking_service.cancel_booking(id, passenger.id, reason)
        
        result = {
            "booking_id": booking.id,
            "status": booking.status.value,
            "cancellation_reason": booking.cancellation_reason
        }
        return success_response("Booking cancelled successfully", data=result)
        
    except BookingNotFoundError:
        return error_response("Booking not found", BOOKING_NOT_FOUND, status_code=404)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@bookings_bp.route('/<string:reference>/boarding-pass', methods=['GET'])
@passenger_required()
def boarding_pass(reference):
    try:
        result = booking_service.get_boarding_pass(reference)
        return success_response("Boarding pass retrieved", data=result)
    except BookingNotFoundError:
        return error_response("Booking not found", BOOKING_NOT_FOUND, status_code=404)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
