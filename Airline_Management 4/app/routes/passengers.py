from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from app.models.passenger import Passenger
from app.schemas import PassengerUpdateSchema
from app.utils.responses import success_response, error_response
from app.utils.decorators import passenger_required
from app.extensions import db
from app.utils.constants import INVALID_INPUT

passengers_bp = Blueprint('passengers_bp', __name__, url_prefix='/api/v1/passengers')

@passengers_bp.route('/me', methods=['GET'])
@passenger_required()
def get_me():
    try:
        user_id = get_jwt_identity()
        passenger = Passenger.query.filter_by(user_id=user_id).first()
        
        result = {
            "first_name": passenger.first_name,
            "last_name": passenger.last_name,
            "date_of_birth": passenger.date_of_birth.isoformat() if passenger.date_of_birth else None,
            "passport_number": passenger.passport_number,
            "nationality": passenger.nationality,
            "phone": passenger.phone,
            "address": passenger.address,
            "created_at": passenger.created_at.isoformat() if passenger.created_at else None
        }
        return success_response("Passenger profile retrieved", data=result)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@passengers_bp.route('/me', methods=['PUT'])
@passenger_required()
def update_me():
    try:
        user_id = get_jwt_identity()
        passenger = Passenger.query.filter_by(user_id=user_id).first()
        
        req_json = request.get_json()
        data = PassengerUpdateSchema().load(req_json)
        
        for key in data.keys():
            if key in req_json:
                setattr(passenger, key, data[key])
                
        db.session.commit()
        
        result = {
            "first_name": passenger.first_name,
            "last_name": passenger.last_name,
            "date_of_birth": passenger.date_of_birth.isoformat() if passenger.date_of_birth else None,
            "passport_number": passenger.passport_number,
            "nationality": passenger.nationality,
            "phone": passenger.phone,
            "address": passenger.address
        }
        return success_response("Passenger profile updated", data=result)
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
