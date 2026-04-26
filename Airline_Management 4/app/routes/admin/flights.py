import string
from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity
from app.models.flight import Flight
from app.models.aircraft import Aircraft, SeatMap, SeatClassEnum
from app.models.airport import Airport
from app.models.flight_status import FlightStatus, FlightStatusEnum
from app.schemas import FlightCreateSchema, FlightUpdateSchema
from app.utils.responses import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.constants import INVALID_INPUT, FLIGHT_NOT_FOUND
from app.exceptions import FlightNotFoundError
from app.extensions import db

admin_flights_bp = Blueprint('admin_flights_bp', __name__, url_prefix='/api/v1/admin')

@admin_flights_bp.route('/flights', methods=['GET'])
@admin_required()
def list_flights():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        source = request.args.get('source')
        destination = request.args.get('destination')
        status = request.args.get('status')
        
        query = Flight.query
        
        from sqlalchemy.orm import aliased
        SourceAirport = aliased(Airport)
        DestinationAirport = aliased(Airport)
        
        query = query.join(SourceAirport, Flight.source_airport_id == SourceAirport.id)
        query = query.join(DestinationAirport, Flight.destination_airport_id == DestinationAirport.id)
        
        if source:
            query = query.filter(SourceAirport.iata_code == source)
        if destination:
            query = query.filter(DestinationAirport.iata_code == destination)
            
        if status:
            query = query.join(FlightStatus).filter(FlightStatus.status == status)
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for f in pagination.items:
            items.append({
                "id": f.id,
                "flight_number": f.flight_number,
                "source": {"iata": f.source_airport.iata_code},
                "destination": {"iata": f.destination_airport.iata_code},
                "aircraft": {"model": f.aircraft.model},
                "departure_time": f.departure_time.isoformat(),
                "arrival_time": f.arrival_time.isoformat(),
                "status": f.status_details.status.value if getattr(f, 'status_details', None) else "scheduled"
            })
            
        return success_response("Flights retrieved", data={
            "items": items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page
        })
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@admin_flights_bp.route('/flights', methods=['POST'])
@admin_required()
def create_flight():
    try:
        req_json = request.get_json()
        data = FlightCreateSchema().load(req_json)
        
        aircraft = Aircraft.query.get(data['aircraft_id'])
        if not aircraft:
            return error_response("Aircraft not found", INVALID_INPUT, status_code=400)
            
        duration = data['arrival_time'] - data['departure_time']
        duration_minutes = int(duration.total_seconds() / 60)
        
        flight = Flight(
            flight_number=data['flight_number'],
            source_airport_id=data['source_airport_id'],
            destination_airport_id=data['destination_airport_id'],
            aircraft_id=data['aircraft_id'],
            departure_time=data['departure_time'],
            arrival_time=data['arrival_time'],
            duration_minutes=duration_minutes,
            base_price_economy=data['base_price_economy'],
            base_price_business=data['base_price_business'],
            base_price_first=data['base_price_first'],
            available_economy=aircraft.economy_seats,
            available_business=aircraft.business_seats,
            available_first=aircraft.first_class_seats,
            is_active=True
        )
        db.session.add(flight)
        db.session.flush()
        
        layout = aircraft.seat_layout
        for seat_class_str, config in layout.items():
            rows_count = config.get('rows', 0)
            cols = config.get('cols', '')
            
            for row in range(1, rows_count + 1):
                for letter in cols:
                    seat_number = f"{row}{letter}"
                    seat_class_enum = getattr(SeatClassEnum, seat_class_str)
                    
                    is_window = letter == cols[0] or letter == cols[-1]
                    is_aisle = False
                    if len(cols) > 2 and letter != cols[0] and letter != cols[-1]:
                        idx = cols.find(letter)
                        if idx == len(cols)//2 - 1 or idx == len(cols)//2:
                            is_aisle = True
                            
                    is_emergency_exit = (row == 1 or row == rows_count)
                    
                    seat_map = SeatMap(
                        flight_id=flight.id,
                        seat_number=seat_number,
                        seat_class=seat_class_enum,
                        is_available=True,
                        is_window=is_window,
                        is_aisle=is_aisle,
                        is_emergency_exit=is_emergency_exit
                    )
                    db.session.add(seat_map)
                    
        flight_status = FlightStatus(
            flight_id=flight.id,
            status=FlightStatusEnum.scheduled
        )
        db.session.add(flight_status)
        db.session.commit()
        
        return success_response("Flight created", data={"id": flight.id}, status_code=201)
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@admin_flights_bp.route('/flights/<int:id>', methods=['PUT'])
@admin_required()
def update_flight(id):
    try:
        flight = Flight.query.get(id)
        if not flight:
            return error_response("Flight not found", FLIGHT_NOT_FOUND, status_code=404)
            
        req_json = request.get_json()
        data = FlightUpdateSchema().load(req_json)
        
        for key in data.keys():
            if key in req_json:
                setattr(flight, key, data[key])
                
        if 'arrival_time' in req_json or 'departure_time' in req_json:
            duration = flight.arrival_time - flight.departure_time
            flight.duration_minutes = int(duration.total_seconds() / 60)
            
        db.session.commit()
        return success_response("Flight updated", data={"id": flight.id})
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@admin_flights_bp.route('/flights/<int:id>', methods=['DELETE'])
@admin_required()
def delete_flight(id):
    try:
        flight = Flight.query.get(id)
        if not flight:
            return error_response("Flight not found", FLIGHT_NOT_FOUND, status_code=404)
            
        flight.is_active = False
        db.session.commit()
        return success_response("Flight deactivated successfully")
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@admin_flights_bp.route('/flights/<int:id>/status', methods=['PUT'])
@admin_required()
def update_status(id):
    try:
        flight = Flight.query.get(id)
        if not flight:
            return error_response("Flight not found", FLIGHT_NOT_FOUND, status_code=404)
            
        req_json = request.get_json()
        user_id = get_jwt_identity()
        
        flight_status = FlightStatus.query.filter_by(flight_id=id).first()
        if not flight_status:
            flight_status = FlightStatus(flight_id=id)
            db.session.add(flight_status)
            
        if 'status' in req_json:
            flight_status.status = getattr(FlightStatusEnum, req_json['status'])
        if 'delay_minutes' in req_json:
            flight_status.delay_minutes = req_json.get('delay_minutes', 0)
        if 'delay_reason' in req_json:
            flight_status.delay_reason = req_json['delay_reason']
        if 'gate_number' in req_json:
            flight_status.gate_number = req_json['gate_number']
        if 'terminal' in req_json:
            flight_status.terminal = req_json['terminal']
            
        flight_status.updated_by = user_id
        db.session.commit()
        
        return success_response("Status updated", data={
            "status": flight_status.status.value,
            "delay_minutes": flight_status.delay_minutes
        })
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
