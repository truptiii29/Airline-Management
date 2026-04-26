import secrets
from datetime import datetime, timedelta, timezone
from app.extensions import db
from app.models.user import User, Role
from app.models.passenger import Passenger
from app.models.otp import OTP, OTPPurposeEnum
from app.exceptions import OTPError
from app.tasks.email_tasks import send_otp_email_task
from flask_jwt_extended import create_access_token, create_refresh_token

BLACKLISTED_TOKENS = set()

def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return jti in BLACKLISTED_TOKENS

def register_user(email, password, first_name, last_name, phone=None, date_of_birth=None, passport_number=None, nationality=None):
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("Email already registered")
        
    passenger_role = Role.query.filter_by(name='passenger').first()
    if not passenger_role:
        passenger_role = Role(name='passenger', description='Passenger Role')
        db.session.add(passenger_role)
        db.session.flush()

    user = User(email=email, role_id=passenger_role.id)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    passenger = Passenger(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        date_of_birth=date_of_birth or datetime.now(timezone.utc).date(),
        passport_number=passport_number or f"TBD-{secrets.token_hex(4)}",
        nationality=nationality or "TBD"
    )
    db.session.add(passenger)
    
    otp_code = str(secrets.randbelow(900000) + 100000)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    otp = OTP(
        user_id=user.id,
        otp_code=otp_code,
        purpose=OTPPurposeEnum.email_verify,
        expires_at=expires_at
    )
    db.session.add(otp)
    db.session.commit()
    
    try:
        send_otp_email_task.delay(user.id, otp_code, OTPPurposeEnum.email_verify.value)
    except Exception:
        pass
    
    print(f"\\n*** DEVELOPMENT MODE: OTP for {user.email} is {otp_code} ***\\n")
    
    return {"user_id": user.id, "email": user.email, "otp_code": otp_code}

def verify_otp(user_id, otp_code, purpose=OTPPurposeEnum.email_verify):
    if isinstance(purpose, str):
        purpose = getattr(OTPPurposeEnum, purpose)
        
    otp = OTP.query.filter(
        OTP.user_id == user_id,
        OTP.is_used == False,
        OTP.expires_at > datetime.now(timezone.utc),
        OTP.purpose == purpose
    ).order_by(OTP.created_at.desc()).first()
    
    if not otp or otp.otp_code != otp_code:
        raise OTPError("Invalid or expired OTP")
        
    otp.is_used = True
    
    user = User.query.get(user_id)
    if purpose == OTPPurposeEnum.email_verify:
        user.is_verified = True
        
    db.session.commit()
    
    passenger = Passenger.query.filter_by(user_id=user.id).first()
    passenger_id = passenger.id if passenger else None
    
    additional_claims = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.name,
        "name": f"{passenger.first_name} {passenger.last_name}" if passenger else None,
        "passenger_id": passenger_id
    }
    
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": additional_claims
    }

def login_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("Invalid credentials")
        
    if not user.is_verified:
        raise OTPError("Email not verified")
        
    if not user.is_active:
        raise ValueError("User account is inactive")
        
    if not user.check_password(password):
        raise ValueError("Invalid credentials")
        
    user.last_login = datetime.now(timezone.utc)
    db.session.commit()
    
    passenger = Passenger.query.filter_by(user_id=user.id).first()
    passenger_id = passenger.id if passenger else None
    
    additional_claims = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.name,
        "name": f"{passenger.first_name} {passenger.last_name}" if passenger else None,
        "passenger_id": passenger_id
    }
    
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims=additional_claims)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": additional_claims
    }

def resend_otp(email, purpose=OTPPurposeEnum.email_verify):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ValueError("User not found")
        
    if isinstance(purpose, str):
        purpose = getattr(OTPPurposeEnum, purpose)
        
    otp_code = str(secrets.randbelow(900000) + 100000)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    otp = OTP(
        user_id=user.id,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expires_at
    )
    db.session.add(otp)
    db.session.commit()
    
    send_otp_email_task.delay(user.id, otp_code, purpose.value)
    return True

def forgot_password(email):
    return resend_otp(email, OTPPurposeEnum.password_reset)

def reset_password(user_id, otp_code, new_password):
    verify_otp(user_id, otp_code, OTPPurposeEnum.password_reset)
    user = User.query.get(user_id)
    user.set_password(new_password)
    db.session.commit()
    return True
