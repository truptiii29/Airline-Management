from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from app.services import seat_service
from app.schemas import SeatLockSchema
from app.utils.responses import success_response, error_response
from app.utils.constants import SEAT_LOCKED, INVALID_INPUT
from app.utils.decorators import passenger_required
from app.exceptions import SeatLockConflictError
from app.models.aircraft import SeatMap, SeatClassEnum
from app.extensions import db
from datetime import datetime, timezone

seats_bp = Blueprint('seats_bp', __name__, url_prefix='/api/v1/seats')

@seats_bp.route('/lock', methods=['POST'])
@passenger_required()
def lock():
    try:
        data = SeatLockSchema().load(request.get_json())
        user_id = get_jwt_identity()
        result = seat_service.SeatService().lock_seat(data['flight_id'], data['seat_number'], user_id)
        return success_response("Seat locked", data=result)
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except SeatLockConflictError as e:
        return error_response(str(e), SEAT_LOCKED, status_code=409)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@seats_bp.route('/unlock/<int:seat_id>', methods=['DELETE'])
@passenger_required()
def unlock(seat_id):
    try:
        user_id = get_jwt_identity()
        success = seat_service.SeatService().release_seat(seat_id, user_id)
        if success:
            return success_response("Seat unlocked successfully")
        return error_response("Not authorized to unlock or seat not found", INVALID_INPUT, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@seats_bp.route('/<int:flight_id>/available', methods=['GET'])
def available(flight_id):
    try:
        now = datetime.now(timezone.utc)
        seats = SeatMap.query.filter(
            SeatMap.flight_id == flight_id,
            SeatMap.is_available == True,
            db.or_(SeatMap.locked_until == None, SeatMap.locked_until < now)
        ).all()
        
        result = {
            "economy": [],
            "business": [],
            "first": []
        }
        
        for seat in seats:
            result[seat.seat_class.value].append({
                "seat_number": seat.seat_number,
                "is_window": seat.is_window,
                "is_aisle": seat.is_aisle,
                "is_emergency_exit": seat.is_emergency_exit
            })
            
        return success_response("Available seats retrieved", data=result)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
