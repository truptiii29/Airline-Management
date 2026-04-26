from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import flight_service, seat_service
from app.utils.responses import success_response, error_response
from app.utils.constants import INVALID_INPUT, FLIGHT_NOT_FOUND
from app.utils.decorators import passenger_required
from app.exceptions import FlightNotFoundError
from app.models.flight_status import FlightStatus

flights_bp = Blueprint('flights_bp', __name__, url_prefix='/api/v1/flights')

@flights_bp.route('/search', methods=['GET'])
def search():
    try:
        source = request.args.get('source')
        destination = request.args.get('destination')
        date_str = request.args.get('date')
        seat_class = request.args.get('seat_class', 'economy')
        
        if not source or not destination or not date_str:
            return error_response("source, destination, and date are required", INVALID_INPUT, status_code=400)
            
        results = flight_service.search_flights(source, destination, date_str, seat_class)
        return success_response("Flights retrieved", data={"results": results, "count": len(results)})
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@flights_bp.route('/', methods=['GET'])
def get_all():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        results = flight_service.get_all_flights(page=page, per_page=per_page)
        return success_response("Flights retrieved", data=results)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@flights_bp.route('/<int:id>', methods=['GET'])
def get_flight(id):
    try:
        result = flight_service.get_flight_by_id(id)
        return success_response("Flight retrieved", data=result)
    except FlightNotFoundError:
        return error_response("Flight not found", FLIGHT_NOT_FOUND, status_code=404)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@flights_bp.route('/<int:id>/seat-map', methods=['GET'])
@passenger_required()
def seat_map(id):
    try:
        current_user_id = get_jwt_identity()
        result = seat_service.SeatService().generate_seat_map(id, current_user_id)
        return success_response("Seat map retrieved", data=result)
    except FlightNotFoundError:
        return error_response("Flight not found", FLIGHT_NOT_FOUND, status_code=404)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@flights_bp.route('/<int:id>/status', methods=['GET'])
def status(id):
    try:
        flight_status = FlightStatus.query.filter_by(flight_id=id).first()
        if not flight_status:
            return error_response("Flight status not found", FLIGHT_NOT_FOUND, status_code=404)
            
        result = {
            "status": flight_status.status.value,
            "delay_minutes": flight_status.delay_minutes,
            "delay_reason": flight_status.delay_reason,
            "gate_number": flight_status.gate_number,
            "terminal": flight_status.terminal,
            "last_updated": flight_status.last_updated.isoformat()
        }
        return success_response("Flight status retrieved", data=result)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
