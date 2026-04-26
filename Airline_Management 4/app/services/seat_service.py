import re
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.flight import Flight
from app.models.aircraft import SeatMap, SeatClassEnum
from app.exceptions import FlightNotFoundError, SeatLockConflictError

class SeatService:
    def generate_seat_map(self, flight_id, current_user_id=None):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise FlightNotFoundError("Flight not found")
            
        seats = SeatMap.query.filter_by(flight_id=flight_id).all()
        
        result = {
            "economy": {"rows": {}},
            "business": {"rows": {}},
            "first": {"rows": {}}
        }
        
        now = datetime.now(timezone.utc)
        
        for seat in seats:
            match = re.match(r'^(\d+)([A-Z]+)$', seat.seat_number)
            if not match:
                continue
                
            row_num = int(match.group(1))
            
            is_locked = False
            if seat.locked_until is not None and seat.locked_until.replace(tzinfo=timezone.utc) > now:
                current_user_id_str = str(current_user_id) if current_user_id else None
                locked_by_str = str(seat.locked_by_user_id) if seat.locked_by_user_id else None
                if locked_by_str != current_user_id_str:
                    is_locked = True
                    
            computed_available = False if is_locked else seat.is_available
            
            seat_obj = {
                "seat_number": seat.seat_number,
                "is_available": computed_available,
                "is_window": seat.is_window,
                "is_aisle": seat.is_aisle,
                "is_emergency_exit": seat.is_emergency_exit,
                "seat_class": seat.seat_class.value,
                "locked": is_locked
            }
            
            class_str = seat.seat_class.value
            if row_num not in result[class_str]["rows"]:
                result[class_str]["rows"][row_num] = []
            
            result[class_str]["rows"][row_num].append(seat_obj)
            
        for cls in result:
            rows_dict = result[cls]["rows"]
            sorted_rows = [{"row": r, "seats": rows_dict[r]} for r in sorted(rows_dict.keys())]
            result[cls]["rows"] = sorted_rows
            
        return result

    def lock_seat(self, flight_id, seat_number, user_id):
        seat = SeatMap.query.filter_by(flight_id=flight_id, seat_number=seat_number).first()
        if not seat:
            raise ValueError("Seat not found")
            
        now = datetime.now(timezone.utc)
        
        # Normalize user_id to string for consistent comparison
        user_id_str = str(user_id)
        
        # Check if seat is booked AND locked by someone else
        if not seat.is_available:
            # Seat is marked unavailable - check if same user can still lock it
            locked_by_str = str(seat.locked_by_user_id) if seat.locked_by_user_id else None
            if locked_by_str and locked_by_str == user_id_str:
                # Same user trying to re-lock their booked seat - allow it
                seat.locked_until = now + timedelta(minutes=30)
                db.session.commit()
                return {"seat_id": seat.id, "locked_until": seat.locked_until.isoformat()}
            else:
                # Different user or no lock - seat is truly unavailable
                raise SeatLockConflictError("Seat already booked")
        
        # Seat is available - check if it's locked by someone else
        if seat.locked_until is not None and seat.locked_until.replace(tzinfo=timezone.utc) > now:
            # Seat lock is still valid
            locked_by_str = str(seat.locked_by_user_id) if seat.locked_by_user_id else None
            if locked_by_str and locked_by_str != user_id_str:
                # Locked by a different user
                raise SeatLockConflictError("Seat is temporarily locked by another user")
        
        # Lock seat for this user (refresh if already locked by them, or lock if expired/unlocked)
        seat.locked_until = now + timedelta(minutes=30)
        seat.locked_by_user_id = user_id_str
        db.session.commit()
        
        return {
            "seat_id": seat.id,
            "locked_until": seat.locked_until.isoformat()
        }

    def release_seat(self, seat_id, user_id):
        seat = SeatMap.query.get(seat_id)
        if not seat:
            return False
            
        user_id_str = str(user_id)
        locked_by_str = str(seat.locked_by_user_id) if seat.locked_by_user_id else None
        
        if locked_by_str == user_id_str:
            seat.locked_until = None
            seat.locked_by_user_id = None
            db.session.commit()
            return True
        return False

    def confirm_seat(self, flight_id, seat_number, user_id):
        seat = SeatMap.query.filter_by(flight_id=flight_id, seat_number=seat_number).first()
        if not seat:
            raise ValueError("Seat not found")
            
        now = datetime.now(timezone.utc)
        
        user_id_str = str(user_id)
        locked_by_str = str(seat.locked_by_user_id) if seat.locked_by_user_id else None
        
        if (locked_by_str != user_id_str or 
            seat.locked_until is None or 
            seat.locked_until.replace(tzinfo=timezone.utc) <= now):
            raise SeatLockConflictError("Seat is not locked by you or lock has expired")
            
        seat.is_available = False
        seat.locked_until = None
        seat.locked_by_user_id = None
        
        flight = Flight.query.get(flight_id)
        class_str = seat.seat_class.value
        attr_name = f"available_{class_str}"
        current_amount = getattr(flight, attr_name)
        if current_amount > 0:
            setattr(flight, attr_name, current_amount - 1)
            
        db.session.commit()
        return True

    @staticmethod
    def get_available_seat_counts(flight_id):
        """
        Get count of available seats by class
        
        Args:
            flight_id: ID of the flight
            
        Returns:
            dict with keys 'economy', 'business', 'first' containing seat counts
        """
        economy_count = SeatMap.query.filter_by(
            flight_id=flight_id, 
            seat_class=SeatClassEnum.ECONOMY, 
            is_available=True
        ).count()
        
        business_count = SeatMap.query.filter_by(
            flight_id=flight_id, 
            seat_class=SeatClassEnum.BUSINESS, 
            is_available=True
        ).count()
        
        first_count = SeatMap.query.filter_by(
            flight_id=flight_id, 
            seat_class=SeatClassEnum.FIRST, 
            is_available=True
        ).count()
        
        return {
            'economy': economy_count,
            'business': business_count,
            'first': first_count
        }
