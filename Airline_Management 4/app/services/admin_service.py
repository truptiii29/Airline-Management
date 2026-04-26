from datetime import datetime, timezone
from sqlalchemy import func, cast, Date
from app.extensions import db
from app.models.flight import Flight
from app.models.booking import Booking
from app.models.payment import Payment, PaymentStatusEnum
from app.models.passenger import Passenger
from app.models.flight_status import FlightStatus, FlightStatusEnum
from app.models.airport import Airport

def get_dashboard_stats():
    now = datetime.now(timezone.utc)
    today = now.date()
    
    active_flights_count = db.session.query(func.count(Flight.id)).filter(Flight.is_active == True).scalar()
    
    today_bookings_count = db.session.query(func.count(Booking.id)).filter(
        cast(Booking.booking_date, Date) == today
    ).scalar()
    
    today_revenue = db.session.query(func.sum(Payment.amount)).filter(
        Payment.payment_status == PaymentStatusEnum.success,
        cast(Payment.payment_date, Date) == today
    ).scalar() or 0.0
    
    total_passengers = db.session.query(func.count(Passenger.id)).scalar()
    
    delayed_flights = db.session.query(func.count(FlightStatus.id)).filter(
        FlightStatus.status == FlightStatusEnum.delayed
    ).scalar()
    
    flights = Flight.query.all()
    total_seats_all = sum(f.aircraft.total_seats for f in flights if f.aircraft)
    available_seats_all = sum(f.available_economy + f.available_business + f.available_first for f in flights)
    
    if total_seats_all > 0:
        booked_seats_all = total_seats_all - available_seats_all
        occupancy_rate = (booked_seats_all / total_seats_all) * 100
    else:
        occupancy_rate = 0.0
        
    top_routes_query = db.session.query(
        Flight.source_airport_id,
        Flight.destination_airport_id,
        func.count(Booking.id).label('booking_count')
    ).join(Booking, Booking.flight_id == Flight.id).group_by(
        Flight.source_airport_id, Flight.destination_airport_id
    ).order_by(db.desc('booking_count')).limit(5).all()
    
    top_routes = []
    for src_id, dst_id, count in top_routes_query:
        src = Airport.query.get(src_id)
        dst = Airport.query.get(dst_id)
        top_routes.append({
            "source": src.iata_code if src else str(src_id),
            "destination": dst.iata_code if dst else str(dst_id),
            "count": count
        })
        
    last_10_bookings_query = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    last_10_bookings = []
    for b in last_10_bookings_query:
        last_10_bookings.append({
            "booking_reference": b.booking_reference,
            "passenger_name": f"{b.passenger.first_name} {b.passenger.last_name}",
            "flight_number": b.flight_details.flight_number,
            "status": b.status.value,
            "booking_date": b.booking_date.isoformat()
        })
        
    return {
        "active_flights": active_flights_count,
        "today_bookings": today_bookings_count,
        "today_revenue": float(today_revenue),
        "total_passengers": total_passengers,
        "delayed_flights": delayed_flights,
        "occupancy_rate": occupancy_rate,
        "top_routes": top_routes,
        "recent_bookings": last_10_bookings
    }

def get_revenue_report(start_date_str, end_date_str, group_by="day"):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    payments = db.session.query(Payment, Booking).join(
        Booking, Payment.booking_id == Booking.id
    ).filter(
        Payment.payment_status == PaymentStatusEnum.success,
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).all()
    
    grouped_data = {}
    total_revenue = 0.0
    
    for payment, booking in payments:
        amount = float(payment.amount)
        total_revenue += amount
        
        if group_by == "day":
            period = payment.payment_date.strftime('%Y-%m-%d')
        elif group_by == "week":
            period = payment.payment_date.strftime('%Y-W%W')
        elif group_by == "month":
            period = payment.payment_date.strftime('%Y-%m')
        else:
            period = payment.payment_date.strftime('%Y-%m-%d')
            
        if period not in grouped_data:
            grouped_data[period] = {"revenue": 0.0, "booking_count": 0}
            
        grouped_data[period]["revenue"] += amount
        grouped_data[period]["booking_count"] += 1
        
    data_list = []
    for period, stats in grouped_data.items():
        data_list.append({
            "period": period,
            "revenue": stats["revenue"],
            "booking_count": stats["booking_count"]
        })
        
    data_list.sort(key=lambda x: x["period"])
    
    return {
        "total_revenue": total_revenue,
        "data": data_list
    }

def get_occupancy_report(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    flights = Flight.query.filter(
        Flight.departure_time >= start_date,
        Flight.departure_time <= end_date
    ).all()
    
    report = []
    
    for flight in flights:
        total_seats = flight.aircraft.total_seats
        available_seats = flight.available_economy + flight.available_business + flight.available_first
        booked_seats = total_seats - available_seats
        
        if total_seats > 0:
            occupancy_percentage = (booked_seats / total_seats) * 100
        else:
            occupancy_percentage = 0.0
            
        report.append({
            "flight_number": flight.flight_number,
            "departure_time": flight.departure_time.isoformat(),
            "source": flight.source_airport.iata_code,
            "destination": flight.destination_airport.iata_code,
            "total_seats": total_seats,
            "booked_seats": booked_seats,
            "occupancy_percentage": occupancy_percentage
        })
        
    report.sort(key=lambda x: x["occupancy_percentage"], reverse=True)
    return report
