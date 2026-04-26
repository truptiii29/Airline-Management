def test_flight_search_valid(client, app):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    res = client.get('/api/v1/flights/search?source=DEL&destination=BOM&date=2026-12-01')
    assert isinstance(res.get_json().get('data', []), list)

def test_flight_search_invalid_iata(client, app):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    res = client.get('/api/v1/flights/search?source=INVALID&destination=BOM&date=2026-12-01')
    assert res.status_code == 200
    assert len(res.get_json()['data']) == 0

def test_get_flights_list(client, app):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    res = client.get('/api/v1/flights/')
    assert res.status_code == 200
    assert 'items' in res.get_json()['data']

def test_get_flight_detail(client, app):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    res = client.get('/api/v1/flights/1')
    assert res.status_code == 200
    assert 'source_airport' in res.get_json()['data']

def test_get_flight_not_found(client):
    res = client.get('/api/v1/flights/999')
    assert res.status_code == 404
    assert res.get_json()['error']['code'] == 'FLIGHT_NOT_FOUND'
