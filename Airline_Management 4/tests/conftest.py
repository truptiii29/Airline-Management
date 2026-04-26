import pytest
from app import create_app
from app.extensions import db
from config import TestingConfig
from app.cli import register_cli_commands
from app.models.user import Role, User
from app.models.otp import OTP

@pytest.fixture
def app():
    app = create_app(config_class=TestingConfig)
    register_cli_commands(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client, app):
    with app.app_context():
        if not Role.query.filter_by(name='passenger').first():
            db.session.add(Role(name='passenger'))
            db.session.commit()
            
    res = client.post('/api/v1/auth/register', json={
        "email": "test@airline.com",
        "password": "Password123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890"
    })
    
    user_id = res.get_json()['data']['user_id']
    
    with app.app_context():
        otp_record = OTP.query.filter_by(user_id=user_id, purpose='email_verify').first()
        otp_code = otp_record.otp_code
        
    client.post('/api/v1/auth/verify-otp', json={
        "user_id": user_id,
        "otp_code": otp_code
    })
    
    login_res = client.post('/api/v1/auth/login', json={
        "email": "test@airline.com",
        "password": "Password123"
    })
    token = login_res.get_json()['data']['access_token']
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(app, client):
    runner = app.test_cli_runner()
    runner.invoke(args=['seed-db'])
    
    login_res = client.post('/api/v1/auth/login', json={
        "email": "admin@airline.com",
        "password": "Admin@123"
    })
    token = login_res.get_json()['data']['access_token']
    
    return {"Authorization": f"Bearer {token}"}
