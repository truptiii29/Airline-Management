import click
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from app.extensions import db
from app.models.user import User, Role
from app.models.passenger import Passenger
from app.models.airport import Airport
from app.models.aircraft import Aircraft, SeatMap, SeatClassEnum
from app.models.flight import Flight
from app.models.flight_status import FlightStatus, FlightStatusEnum
from app.models.booking import Booking, BookingStatusEnum, BookingClassEnum

def register_cli_commands(app):
    @app.cli.command("seed-db")
    def seed_db():
        """Seeds the database with initial data."""
        airports_data = [
            {"iata": "DEL", "name": "Indira Gandhi International", "city": "New Delhi", "country": "India", "tz": "Asia/Kolkata"},
            {"iata": "BOM", "name": "Chhatrapati Shivaji Maharaj", "city": "Mumbai", "country": "India", "tz": "Asia/Kolkata"},
            {"iata": "MAA", "name": "Chennai International", "city": "Chennai", "country": "India", "tz": "Asia/Kolkata"},
            {"iata": "BLR", "name": "Kempegowda International", "city": "Bengaluru", "country": "India", "tz": "Asia/Kolkata"},
            {"iata": "CCU", "name": "Netaji Subhas Chandra Bose", "city": "Kolkata", "country": "India", "tz": "Asia/Kolkata"}
        ]
        
        airports = {}
        for a in airports_data:
            ap = Airport(iata_code=a['iata'], name=a['name'], city=a['city'], country=a['country'], timezone=a['tz'])
            db.session.add(ap)
            airports[a['iata']] = ap
        db.session.flush()

        layout = {
            "economy": {"rows": 20, "cols": "ABCDEF"},
            "business": {"rows": 6, "cols": "ACDF"},
            "first": {"rows": 3, "cols": "AD"}
        }
        total_economy = 20 * 6
        total_business = 6 * 4
        total_first = 3 * 2
        total_seats = total_economy + total_business + total_first
        
        aircraft_list = []
        for i in range(3):
            ac = Aircraft(
                registration_number=f"VT-AL{i+1}",
                model=f"Boeing 737-{800+i*100}",
                total_seats=total_seats,
                economy_seats=total_economy,
                business_seats=total_business,
                first_class_seats=total_first,
                seat_layout=layout
            )
            db.session.add(ac)
            aircraft_list.append(ac)
        db.session.flush()
        
        import random
        now = datetime.now(timezone.utc)
        routes = [("DEL", "BOM"), ("BOM", "DEL"), ("DEL", "BLR"), ("BLR", "DEL"), ("BOM", "MAA")]
        
        for i in range(10):
            src_iata, dest_iata = random.choice(routes)
            src = airports[src_iata]
            dest = airports[dest_iata]
            ac = random.choice(aircraft_list)
            
            dep_time = now + timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
            arr_time = dep_time + timedelta(hours=2, minutes=random.randint(0, 30))
            
            flight = Flight(
                flight_number=f"AL-{100+i}",
                source_airport_id=src.id,
                destination_airport_id=dest.id,
                aircraft_id=ac.id,
                departure_time=dep_time,
                arrival_time=arr_time,
                duration_minutes=int((arr_time - dep_time).total_seconds() / 60),
                base_price_economy=5000.00,
                base_price_business=15000.00,
                base_price_first=25000.00,
                available_economy=ac.economy_seats,
                available_business=ac.business_seats,
                available_first=ac.first_class_seats,
                is_active=True
            )
            db.session.add(flight)
            db.session.flush()
            
            fs = FlightStatus(flight_id=flight.id, status=FlightStatusEnum.scheduled)
            db.session.add(fs)
            
            current_row = 1
            for seat_class_str, config in ac.seat_layout.items():
                rows_count = config.get('rows', 0)
                cols = config.get('cols', '')
                seat_class_enum = getattr(SeatClassEnum, seat_class_str)
                
                for row in range(current_row, current_row + rows_count):
                    for letter in cols:
                        seat_number = f"{row}{letter}"
                        is_window = letter == cols[0] or letter == cols[-1]
                        is_emergency_exit = (row == current_row or row == current_row + rows_count - 1)
                        is_aisle = False
                        if len(cols) > 2 and letter != cols[0] and letter != cols[-1]:
                            idx = cols.find(letter)
                            if idx == len(cols)//2 - 1 or idx == len(cols)//2:
                                is_aisle = True
                                
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
                current_row += rows_count
        db.session.flush()
        
        admin_role = Role.query.filter_by(name='admin').first() or Role(name='admin', description='Admin')
        passenger_role = Role.query.filter_by(name='passenger').first() or Role(name='passenger', description='Passenger')
        db.session.add_all([admin_role, passenger_role])
        db.session.flush()
        
        admin_user = User(email='admin@airline.com', role_id=admin_role.id, is_verified=True)
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        
        passenger_user = User(email='passenger@airline.com', role_id=passenger_role.id, is_verified=True)
        passenger_user.set_password('Pass@123')
        db.session.add(passenger_user)
        db.session.flush()
        
        passenger_profile = Passenger(
            user_id=passenger_user.id,
            first_name='John',
            last_name='Doe',
            date_of_birth=datetime(1990, 1, 1).date(),
            passport_number='A12345678',
            nationality='Indian',
            phone='9876543210'
        )
        db.session.add(passenger_profile)
        db.session.flush()
        
        flights = Flight.query.limit(3).all()
        for i, flight in enumerate(flights):
            seat = SeatMap.query.filter_by(flight_id=flight.id, is_available=True).first()
            if seat:
                seat.is_available = False
                
                b = Booking(
                    booking_reference=f"REF00{i}",
                    passenger_id=passenger_profile.id,
                    flight_id=flight.id,
                    seat_number=seat.seat_number,
                    seat_class=getattr(BookingClassEnum, seat.seat_class.name),
                    status=BookingStatusEnum.confirmed,
                    total_amount=5000.00
                )
                db.session.add(b)
        
        db.session.commit()
        print("Database seeded successfully.")

    @app.cli.command("check-db")
    def check_db():
        """Checks the database connection."""
        try:
            db.session.execute(text("SELECT 1"))
            db_host = app.config.get('DB_HOST', 'unknown')
            print(f"connected successfully to MySQL at the {db_host} value")
        except Exception as e:
            print(f"Failed to connect to database: {str(e)}")

    @app.cli.command("cleanup-locks")
    def cleanup_locks():
        """Cleans up expired seat locks."""
        now = datetime.now(timezone.utc)
        seats = SeatMap.query.filter(
            SeatMap.locked_until != None,
            SeatMap.locked_until < now
        ).all()
        
        count = len(seats)
        for seat in seats:
            seat.locked_until = None
            seat.locked_by_user_id = None
            
        db.session.commit()
        print(f"Released {count} expired seat locks.")
