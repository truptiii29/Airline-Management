from flask import Blueprint
from app.models.flight_status import FlightStatus
from app.utils.responses import success_response, error_response
from app.utils.constants import FLIGHT_NOT_FOUND
from app.extensions import db

flight_status_bp = Blueprint('flight_status_bp', __name__, url_prefix='/api/v1/flight-status')

@flight_status_bp.route('/<int:flight_id>', methods=['GET'])
def get_status(flight_id):
    try:
        flight_status = FlightStatus.query.filter_by(flight_id=flight_id).first()
        if not flight_status:
            return error_response("Flight status not found", FLIGHT_NOT_FOUND, status_code=404)
            
        result = {
            "flight_id": flight_status.flight_id,
            "status": flight_status.status.value,
            "delay_minutes": flight_status.delay_minutes,
            "delay_reason": flight_status.delay_reason,
            "gate_number": flight_status.gate_number,
            "terminal": flight_status.terminal,
            "last_updated": flight_status.last_updated.isoformat(),
            "flight_number": flight_status.flight.flight_number
        }
        return success_response("Flight status retrieved", data=result)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
