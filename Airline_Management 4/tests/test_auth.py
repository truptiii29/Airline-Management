import pytest
from datetime import datetime, timedelta, timezone
from app.models.otp import OTP
from app.extensions import db

def test_successful_registration(client, app):
    with app.app_context():
        from app.models.user import Role
        db.session.add(Role(name='passenger'))
        db.session.commit()
        
    res = client.post('/api/v1/auth/register', json={
        "email": "newuser@airline.com",
        "password": "Password123",
        "first_name": "New",
        "last_name": "User"
    })
    assert res.status_code == 201
    assert "Registration successful" in res.get_json()['message']

def test_duplicate_email_registration(client, app):
    with app.app_context():
        from app.models.user import Role
        db.session.add(Role(name='passenger'))
        db.session.commit()
    
    payload = {
        "email": "dup@airline.com",
        "password": "Password123",
        "first_name": "Dup",
        "last_name": "User"
    }
    client.post('/api/v1/auth/register', json=payload)
    res = client.post('/api/v1/auth/register', json=payload)
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'INVALID_INPUT'

def test_login_before_otp_verify(client, app):
    with app.app_context():
        from app.models.user import Role
        db.session.add(Role(name='passenger'))
        db.session.commit()
        
    client.post('/api/v1/auth/register', json={
        "email": "unverified@airline.com",
        "password": "Password123",
        "first_name": "Unverified",
        "last_name": "User"
    })
    
    res = client.post('/api/v1/auth/login', json={
        "email": "unverified@airline.com",
        "password": "Password123"
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'EMAIL_NOT_VERIFIED'

def test_otp_verify_expired(client, app):
    with app.app_context():
        from app.models.user import Role
        db.session.add(Role(name='passenger'))
        db.session.commit()
        
    res = client.post('/api/v1/auth/register', json={
        "email": "expired@airline.com",
        "password": "Password123",
        "first_name": "Expired",
        "last_name": "User"
    })
    user_id = res.get_json()['data']['user_id']
    
    with app.app_context():
        otp_record = OTP.query.filter_by(user_id=user_id, purpose='email_verify').first()
        otp_code = otp_record.otp_code
        otp_record.expires_at = datetime.now(timezone.utc) - timedelta(minutes=10)
        db.session.commit()
        
    res = client.post('/api/v1/auth/verify-otp', json={
        "user_id": user_id,
        "otp_code": otp_code
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'OTP_EXPIRED'

def test_otp_verify_wrong_code(client, app):
    with app.app_context():
        from app.models.user import Role
        db.session.add(Role(name='passenger'))
        db.session.commit()
        
    res = client.post('/api/v1/auth/register', json={
        "email": "wrongotp@airline.com",
        "password": "Password123",
        "first_name": "Wrong",
        "last_name": "OTP"
    })
    user_id = res.get_json()['data']['user_id']
    
    res = client.post('/api/v1/auth/verify-otp', json={
        "user_id": user_id,
        "otp_code": "000000"
    })
    assert res.status_code == 400
    assert res.get_json()['error']['code'] == 'OTP_INVALID'

def test_successful_login(client, app):
    with app.app_context():
        from app.models.user import Role
        db.session.add(Role(name='passenger'))
        db.session.commit()
        
    res = client.post('/api/v1/auth/register', json={
        "email": "success@airline.com",
        "password": "Password123",
        "first_name": "Success",
        "last_name": "User"
    })
    user_id = res.get_json()['data']['user_id']
    
    with app.app_context():
        otp_record = OTP.query.filter_by(user_id=user_id, purpose='email_verify').first()
        otp_code = otp_record.otp_code
        
    client.post('/api/v1/auth/verify-otp', json={
        "user_id": user_id,
        "otp_code": otp_code
    })
    
    res = client.post('/api/v1/auth/login', json={
        "email": "success@airline.com",
        "password": "Password123"
    })
    assert res.status_code == 200
    data = res.get_json()['data']
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_wrong_password(client, app):
    with app.app_context():
        from app.models.user import Role
        db.session.add(Role(name='passenger'))
        db.session.commit()
        
    res = client.post('/api/v1/auth/register', json={
        "email": "wrongpass@airline.com",
        "password": "Password123",
        "first_name": "Wrong",
        "last_name": "Pass"
    })
    user_id = res.get_json()['data']['user_id']
    
    with app.app_context():
        otp_record = OTP.query.filter_by(user_id=user_id, purpose='email_verify').first()
        otp_code = otp_record.otp_code
        
    client.post('/api/v1/auth/verify-otp', json={
        "user_id": user_id,
        "otp_code": otp_code
    })
    
    res = client.post('/api/v1/auth/login', json={
        "email": "wrongpass@airline.com",
        "password": "WrongPassword123"
    })
    assert res.status_code == 401
