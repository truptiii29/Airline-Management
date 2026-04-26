import secrets
from datetime import datetime, timezone
from app.extensions import db
from app.models.flight import Flight
from app.models.aircraft import SeatMap
from app.models.booking import Booking, BookingStatusEnum, BookingClassEnum
from app.models.payment import PaymentStatusEnum
from app.exceptions import FlightNotFoundError, SeatLockConflictError, BookingNotFoundError
from app.tasks.email_tasks import send_cancellation_email_task

def create_booking(passenger_id, flight_id, seat_number, seat_class, user_id):
    flight = Flight.query.get(flight_id)
    if not flight or not flight.is_active:
        raise FlightNotFoundError("Flight not found or inactive")
        
    seat = SeatMap.query.filter_by(flight_id=flight_id, seat_number=seat_number).first()
    if not seat:
        raise ValueError("Seat not found")
        
    now = datetime.now(timezone.utc)
    
    # Convert to string for comparison
    user_id_str = str(user_id)
    locked_by_str = str(seat.locked_by_user_id) if seat.locked_by_user_id else None
    
    if (locked_by_str != user_id_str or 
        seat.locked_until is None or 
        seat.locked_until.replace(tzinfo=timezone.utc) <= now):
        raise SeatLockConflictError("Seat must be locked by you before booking")
        
    price = float(getattr(flight, f"base_price_{seat_class}"))
    
    booking_reference = None
    while True:
        ref = secrets.token_urlsafe(5).upper()[:7]
        if not Booking.query.filter_by(booking_reference=ref).first():
            booking_reference = ref
            break
            
    booking = Booking(
        booking_reference=booking_reference,
        passenger_id=passenger_id,
        flight_id=flight_id,
        seat_number=seat_number,
        seat_class=getattr(BookingClassEnum, seat_class),
        status=BookingStatusEnum.pending,
        total_amount=price
    )
    db.session.add(booking)
    db.session.commit()
    
    # ✅ FIX 2: Decrement available seat count
    available_col = f"available_{seat_class}"
    current = getattr(flight, available_col)
    setattr(flight, available_col, current - 1)
    db.session.commit()
    
    # ✅ BROADCAST SEAT UPDATE VIA SOCKET
    try:
        from app.services.socket_service import broadcast_seat_update, broadcast_seat_count_update
        from app.services.seat_service import SeatService
        
        seat_data = {
            'seat_number': seat.seat_number,
            'seat_class': seat.seat_class.value,
            'is_available': False
        }
        broadcast_seat_update(flight_id, seat_data, action='booked')
        
        # Broadcast updated seat counts
        seat_counts = SeatService.get_available_seat_counts(flight_id)
        broadcast_seat_count_update(flight_id, seat_counts)
    except Exception as e:
        print(f"⚠️ Socket broadcast error: {str(e)}")
    
    return booking

def cancel_booking(booking_id, passenger_id, reason=None):
    from app.services.payment_service import PaymentService
    
    booking = Booking.query.filter_by(id=booking_id, passenger_id=passenger_id).first()
    if not booking:
        raise BookingNotFoundError("Booking not found")
        
    if booking.status not in [BookingStatusEnum.pending, BookingStatusEnum.confirmed]:
        raise BookingNotFoundError("Cannot cancel a completed or already cancelled booking")
        
    booking.status = BookingStatusEnum.cancelled
    booking.cancelled_at = datetime.now(timezone.utc)
    booking.cancellation_reason = reason
    
    seat = SeatMap.query.filter_by(flight_id=booking.flight_id, seat_number=booking.seat_number).first()
    if seat:
        seat.is_available = True
        seat.locked_until = None
        seat.locked_by_user_id = None
        
    flight = Flight.query.get(booking.flight_id)
    class_str = booking.seat_class.value
    attr_name = f"available_{class_str}"
    current_amount = getattr(flight, attr_name)
    setattr(flight, attr_name, current_amount + 1)
    
    if booking.payment and booking.payment.payment_status == PaymentStatusEnum.success:
        PaymentService().process_refund(booking.payment.id)
        
    db.session.commit()
    
    send_cancellation_email_task.delay(booking.id)
    
    return booking

def get_boarding_pass(booking_reference):
    booking = Booking.query.filter_by(booking_reference=booking_reference).first()
    if not booking:
        raise BookingNotFoundError("Booking not found")
        
    passenger = booking.passenger
    flight = booking.flight_details
    status_details = flight.status_details if flight else None
    
    return {
        "booking_reference": booking.booking_reference,
        "passenger_name": f"{passenger.first_name} {passenger.last_name}",
        "flight_number": flight.flight_number,
        "from": {
            "iata": flight.source_airport.iata_code,
            "city": flight.source_airport.city,
            "terminal": status_details.terminal if status_details else None
        },
        "to": {
            "iata": flight.destination_airport.iata_code,
            "city": flight.destination_airport.city,
            "terminal": None
        },
        "departure_time": flight.departure_time.isoformat(),
        "arrival_time": flight.arrival_time.isoformat(),
        "seat": booking.seat_number,
        "seat_class": booking.seat_class.value,
        "gate": status_details.gate_number if status_details else None,
        "status": status_details.status.value if status_details else "scheduled"
    }
