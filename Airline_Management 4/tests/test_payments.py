def test_initiate_payment(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    client.post('/api/v1/seats/lock', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2A"
    })
    booking_res = client.post('/api/v1/bookings/', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2A",
        "seat_class": "economy"
    })
    booking_id = booking_res.get_json()['data']['id']
    
    res = client.post('/api/v1/payments/initiate', headers=auth_headers, json={
        "booking_id": booking_id,
        "payment_method": "credit_card"
    })
    assert res.status_code == 200
    assert 'transaction_id' in res.get_json()['data']

def test_confirm_payment_success(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    client.post('/api/v1/seats/lock', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2B"
    })
    booking_res = client.post('/api/v1/bookings/', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2B",
        "seat_class": "economy"
    })
    booking_id = booking_res.get_json()['data']['id']
    
    pay_res = client.post('/api/v1/payments/initiate', headers=auth_headers, json={
        "booking_id": booking_id,
        "payment_method": "credit_card"
    })
    transaction_id = pay_res.get_json()['data']['transaction_id']
    
    res = client.post('/api/v1/payments/confirm', headers=auth_headers, json={
        "transaction_id": transaction_id,
        "gateway_response": {"status": "success"}
    })
    assert res.status_code == 200
    assert res.get_json()['data']['payment_status'] == 'completed'
    
    booking = client.get('/api/v1/bookings/', headers=auth_headers).get_json()['data']
    assert any(b['id'] == booking_id and b['status'] == 'confirmed' for b in booking)

def test_confirm_payment_failed(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    client.post('/api/v1/seats/lock', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2C"
    })
    booking_res = client.post('/api/v1/bookings/', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2C",
        "seat_class": "economy"
    })
    booking_id = booking_res.get_json()['data']['id']
    
    pay_res = client.post('/api/v1/payments/initiate', headers=auth_headers, json={
        "booking_id": booking_id,
        "payment_method": "credit_card"
    })
    transaction_id = pay_res.get_json()['data']['transaction_id']
    
    res = client.post('/api/v1/payments/confirm', headers=auth_headers, json={
        "transaction_id": transaction_id,
        "gateway_response": {"status": "failed"}
    })
    assert res.status_code == 400
    
def test_refund_calculation(client, app, auth_headers):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    client.post('/api/v1/seats/lock', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2D"
    })
    booking_res = client.post('/api/v1/bookings/', headers=auth_headers, json={
        "flight_id": 1,
        "seat_number": "2D",
        "seat_class": "economy"
    })
    booking_id = booking_res.get_json()['data']['id']
    
    pay_res = client.post('/api/v1/payments/initiate', headers=auth_headers, json={
        "booking_id": booking_id,
        "payment_method": "credit_card"
    })
    transaction_id = pay_res.get_json()['data']['transaction_id']
    
    client.post('/api/v1/payments/confirm', headers=auth_headers, json={
        "transaction_id": transaction_id,
        "gateway_response": {"status": "success"}
    })
    
    res = client.post(f'/api/v1/bookings/{booking_id}/cancel', headers=auth_headers)
    assert res.status_code == 200
    assert 'refund_amount' in res.get_json()['data']
