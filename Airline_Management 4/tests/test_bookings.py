def test_create_booking_no_auth(client):
    res = client.post('/api/v1/bookings/', json={
        "flight_id": 1,
        "seat_number": "1A",
        "seat_class": "economy"
    })
    assert res.status_code == 401

def test_create_booking_with_auth(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    client.post('/api/v1/seats/lock', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "1A"
    })
    
    res = client.post('/api/v1/bookings/', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "1A",
        "seat_class": "economy"
    })
    assert res.status_code == 201
    assert 'booking_reference' in res.get_json()['data']

def test_get_my_bookings(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    res = client.get('/api/v1/bookings/', headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.get_json()['data'], list)

def test_cancel_booking(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    client.post('/api/v1/seats/lock', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "1B"
    })
    booking_res = client.post('/api/v1/bookings/', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "1B",
        "seat_class": "economy"
    })
    booking_id = booking_res.get_json()['data']['id']
    
    res = client.post(f'/api/v1/bookings/{booking_id}/cancel', headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()['data']['status'] == 'cancelled'

def test_get_boarding_pass(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    client.post('/api/v1/seats/lock', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "1C"
    })
    booking_res = client.post('/api/v1/bookings/', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "1C",
        "seat_class": "economy"
    })
    booking_id = booking_res.get_json()['data']['id']
    
    # Needs payment success before boarding pass actually
    # Mocking or assuming simple flow where confirmed status isn't strictly required for boarding pass test due to mocked seeds?
    # Booking creates with 'pending', let's set it to 'confirmed' for test.
    with app.app_context():
        from app.models.booking import Booking
        from app.extensions import db
        b = Booking.query.get(booking_id)
        b.status = "confirmed"
        db.session.commit()
    
    res = client.get(f'/api/v1/bookings/{booking_id}/boarding-pass', headers=auth_headers)
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'passenger_name' in data
    assert 'flight_number' in data
    assert 'seat' in data
    assert 'status' in data
