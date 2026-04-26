from datetime import datetime
from sqlalchemy import cast, Date
from sqlalchemy.orm import aliased
from app.extensions import db
from app.models.flight import Flight
from app.models.airport import Airport
from app.exceptions import FlightNotFoundError

def search_flights(source, destination, date_str, seat_class='economy'):
    SourceAirport = aliased(Airport)
    DestinationAirport = aliased(Airport)
    
    parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    query = db.session.query(Flight).join(
        SourceAirport, Flight.source_airport_id == SourceAirport.id
    ).join(
        DestinationAirport, Flight.destination_airport_id == DestinationAirport.id
    ).filter(
        SourceAirport.iata_code == source,
        DestinationAirport.iata_code == destination,
        cast(Flight.departure_time, Date) == parsed_date,
        Flight.is_active == True,
        getattr(Flight, f"available_{seat_class}") > 0
    ).distinct().order_by(Flight.departure_time)
    
    flights = query.all()
    results = []
    
    for f in flights:
        hours = f.duration_minutes // 60
        minutes = f.duration_minutes % 60
        duration_display = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
        
        price = float(getattr(f, f"base_price_{seat_class}"))
        available_seats = getattr(f, f"available_{seat_class}")
        
        results.append({
            "flight_id": f.id,
            "flight_number": f.flight_number,
            "source": {
                "iata": f.source_airport.iata_code,
                "name": f.source_airport.name,
                "city": f.source_airport.city
            },
            "destination": {
                "iata": f.destination_airport.iata_code,
                "name": f.destination_airport.name,
                "city": f.destination_airport.city
            },
            "departure_time": f.departure_time.isoformat(),
            "arrival_time": f.arrival_time.isoformat(),
            "duration_display": duration_display,
            "prices": {
                "economy": float(f.base_price_economy),
                "business": float(f.base_price_business),
                "first": float(f.base_price_first)
            },
            "base_price_economy": float(f.base_price_economy),
            "base_price_business": float(f.base_price_business),
            "base_price_first": float(f.base_price_first),
            "price": price,
            "available_seats": available_seats
        })
        
    return results

def get_flight_by_id(flight_id):
    flight = Flight.query.get(flight_id)
    if not flight:
        raise FlightNotFoundError("Flight not found")
        
    return {
        "id": flight.id,
        "flight_number": flight.flight_number,
        "source_airport": {
            "id": flight.source_airport.id,
            "iata_code": flight.source_airport.iata_code,
            "name": flight.source_airport.name,
            "city": flight.source_airport.city,
            "country": flight.source_airport.country,
            "timezone": flight.source_airport.timezone
        },
        "destination_airport": {
            "id": flight.destination_airport.id,
            "iata_code": flight.destination_airport.iata_code,
            "name": flight.destination_airport.name,
            "city": flight.destination_airport.city,
            "country": flight.destination_airport.country,
            "timezone": flight.destination_airport.timezone
        },
        "aircraft": {
            "id": flight.aircraft.id,
            "registration_number": flight.aircraft.registration_number,
            "model": flight.aircraft.model
        },
        "departure_time": flight.departure_time.isoformat(),
        "arrival_time": flight.arrival_time.isoformat(),
        "duration_minutes": flight.duration_minutes,
        "base_price_economy": float(flight.base_price_economy),
        "base_price_business": float(flight.base_price_business),
        "base_price_first": float(flight.base_price_first),
        "available_economy": flight.available_economy,
        "available_business": flight.available_business,
        "available_first": flight.available_first,
        "is_active": flight.is_active
    }

def get_all_flights(page=1, per_page=10):
    pagination = Flight.query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = []
    for f in pagination.items:
        items.append({
            "id": f.id,
            "flight_number": f.flight_number,
            "departure_time": f.departure_time.isoformat(),
            "arrival_time": f.arrival_time.isoformat(),
            "source": f.source_airport.iata_code,
            "destination": f.destination_airport.iata_code,
            "base_price_economy": float(f.base_price_economy),
            "base_price_business": float(f.base_price_business),
            "base_price_first": float(f.base_price_first)
        })
        
    return {
        "items": items,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }
