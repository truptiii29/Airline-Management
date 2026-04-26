from app.models.user import Role, User
from app.models.passenger import Passenger
from app.models.airport import Airport
from app.models.aircraft import Aircraft, SeatMap
from app.models.flight import Flight
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.flight_status import FlightStatus
from app.models.otp import OTP

__all__ = [
    'Role', 'User', 'Passenger', 'Airport',
    'Aircraft', 'SeatMap', 'Flight', 'Booking',
    'Payment', 'FlightStatus', 'OTP'
]
