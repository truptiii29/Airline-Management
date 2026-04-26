from app import create_app
from app.services.seat_service import SeatService
from app.services.booking_service import create_booking

app = create_app()
with app.app_context():
    try:
        SeatService().lock_seat(1, "9B", 2)
        print("Lock Success")
        create_booking(1, 1, "9B", "economy", 2)
        print("Booking Success")
    except Exception as e:
        import traceback
        traceback.print_exc()
