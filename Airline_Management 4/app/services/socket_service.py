"""Socket.IO service for real-time seat updates"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from datetime import datetime, timezone

socketio = SocketIO(cors_allowed_origins="*")

# Store active connections per flight
active_users = {}

def init_socket(app):
    """Initialize Socket.IO with Flask app"""
    socketio.init_app(app)
    return socketio


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"✅ Client connected: {request.sid}")
    emit('connection_response', {
        'data': 'Connected to real-time seat updates',
        'timestamp': str(datetime.now(timezone.utc))
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"❌ Client disconnected: {request.sid}")
    
    # Remove user from all flights
    for flight_id in list(active_users.keys()):
        if request.sid in active_users[flight_id]:
            active_users[flight_id].remove(request.sid)
            if not active_users[flight_id]:
                del active_users[flight_id]


@socketio.on('join_flight')
def on_join_flight(data):
    """User joins a flight's seat update channel"""
    flight_id = data.get('flight_id')
    room = f'flight_{flight_id}'
    join_room(room)
    
    if flight_id not in active_users:
        active_users[flight_id] = []
    active_users[flight_id].append(request.sid)
    
    print(f"👤 User joined flight {flight_id} (Room: {room})")
    print(f"   Active users on flight {flight_id}: {len(active_users.get(flight_id, []))}")
    
    emit('joined_flight', {
        'flight_id': flight_id,
        'message': 'Joined seat updates',
        'active_users': len(active_users.get(flight_id, []))
    })


@socketio.on('leave_flight')
def on_leave_flight(data):
    """User leaves a flight's seat update channel"""
    flight_id = data.get('flight_id')
    room = f'flight_{flight_id}'
    leave_room(room)
    
    if flight_id in active_users and request.sid in active_users[flight_id]:
        active_users[flight_id].remove(request.sid)
        if not active_users[flight_id]:
            del active_users[flight_id]
    
    print(f"👤 User left flight {flight_id}")


def broadcast_seat_update(flight_id, seat_data, action='booked'):
    """
    Broadcast seat update to all users watching this flight
    
    Args:
        flight_id: ID of the flight
        seat_data: Dict with seat info {seat_number, seat_class, is_available}
        action: 'booked', 'unlocked', 'available'
    """
    room = f'flight_{flight_id}'
    socketio.emit('seat_update', {
        'flight_id': flight_id,
        'seat': seat_data,
        'action': action,
        'timestamp': str(datetime.now(timezone.utc))
    }, room=room)
    print(f"🪑 Broadcasted: Seat {seat_data.get('seat_number')} - {action} (Flight {flight_id})")


def broadcast_seat_count_update(flight_id, seat_counts):
    """
    Broadcast updated seat counts to all users
    
    Args:
        flight_id: ID of the flight
        seat_counts: Dict with counts {economy, business, first}
    """
    room = f'flight_{flight_id}'
    socketio.emit('seat_count_update', {
        'flight_id': flight_id,
        'seat_counts': seat_counts,
        'timestamp': str(datetime.now(timezone.utc))
    }, room=room)
    print(f"📊 Broadcasted seat counts for flight {flight_id}: {seat_counts}")
