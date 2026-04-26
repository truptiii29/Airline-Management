from flask import Blueprint, request
from app.models.booking import Booking
from app.models.passenger import Passenger
from app.models.flight import Flight
from app.models.airport import Airport
from app.models.payment import Payment
from app.utils.responses import success_response, error_response
from app.utils.decorators import admin_required
from app.extensions import db

admin_bookings_bp = Blueprint('admin_bookings_bp', __name__, url_prefix='/api/v1/admin')

@admin_bookings_bp.route('/bookings', methods=['GET'])
@admin_required()
def list_bookings():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        flight_id = request.args.get('flight_id')
        
        query = Booking.query.join(Passenger).join(Flight)
        
        if status:
            query = query.filter(Booking.status == status)
        if start_date and end_date:
            query = query.filter(Booking.booking_date.between(start_date, end_date))
        if flight_id:
            query = query.filter(Booking.flight_id == flight_id)
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for b in pagination.items:
            items.append({
                "booking_reference": b.booking_reference,
                "passenger_name": f"{b.passenger.first_name} {b.passenger.last_name}",
                "flight_number": b.flight_details.flight_number,
                "source_iata": b.flight_details.source_airport.iata_code,
                "destination_iata": b.flight_details.destination_airport.iata_code,
                "seat_number": b.seat_number,
                "seat_class": b.seat_class.value,
                "status": b.status.value,
                "booking_date": b.booking_date.isoformat(),
                "total_amount": float(b.total_amount),
                "payment_status": b.payment.payment_status.value if b.payment else None
            })
            
        return success_response("Bookings retrieved", data={
            "items": items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page
        })
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
