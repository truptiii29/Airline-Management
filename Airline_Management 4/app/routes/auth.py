from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from app.services import auth_service
from app.schemas import AuthRegisterSchema, AuthLoginSchema, OTPVerifySchema, PasswordResetSchema
from app.utils.responses import success_response, error_response
from app.utils.constants import INVALID_INPUT, OTP_EXPIRED, OTP_INVALID
from app.exceptions import OTPError
from app.services.auth_service import BLACKLISTED_TOKENS

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = AuthRegisterSchema().load(request.get_json())
        result = auth_service.register_user(**data)
        return success_response("Registration successful. Please check your email for OTP", data=result, status_code=201)
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except ValueError as e:
        if "Email already registered" in str(e):
            return error_response("Email already registered", INVALID_INPUT, status_code=400)
        return error_response(str(e), INVALID_INPUT, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = AuthLoginSchema().load(request.get_json())
        result = auth_service.login_user(data['email'], data['password'])
        return success_response("Login successful", data=result)
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except OTPError as e:
        return error_response(str(e), "OTP_ERROR", status_code=403)
    except ValueError as e:
        return error_response("Invalid credentials", "UNAUTHORIZED", status_code=401)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = OTPVerifySchema().load(request.get_json())
        result = auth_service.verify_otp(data['user_id'], data['otp_code'], data.get('purpose', 'email_verify'))
        return success_response("OTP verified successfully", data=result)
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except OTPError as e:
        if "expired" in str(e).lower():
            return error_response("OTP expired", OTP_EXPIRED, status_code=400)
        return error_response("Invalid OTP", OTP_INVALID, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    try:
        user_id = request.get_json().get('user_id')
        if not user_id:
            return error_response("user_id is required", INVALID_INPUT, status_code=400)
            
        from app.models.user import User
        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", INVALID_INPUT, status_code=400)
            
        auth_service.resend_otp(user.email)
        return success_response("OTP resent successfully")
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return success_response("Token refreshed", data={"access_token": access_token})
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        BLACKLISTED_TOKENS.add(jti)
        return success_response("Logged out successfully")
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        email = request.get_json().get('email')
        if not email:
            return error_response("email is required", INVALID_INPUT, status_code=400)
        
        try:
            auth_service.forgot_password(email)
        except ValueError:
            pass # Suppress error to prevent enumeration
            
        return success_response("Password reset OTP sent to your email")
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = PasswordResetSchema().load(request.get_json())
        auth_service.reset_password(data['user_id'], data['otp_code'], data['new_password'])
        return success_response("Password reset successful")
    except ValidationError as e:
        return error_response(str(e.messages), INVALID_INPUT, status_code=400)
    except OTPError as e:
        return error_response(str(e), OTP_INVALID, status_code=400)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
