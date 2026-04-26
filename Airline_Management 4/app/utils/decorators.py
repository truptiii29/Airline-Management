from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from app.utils.responses import error_response
from app.utils.constants import UNAUTHORIZED, EMAIL_NOT_VERIFIED

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "admin":
                return error_response("Admin privilege required", UNAUTHORIZED, status_code=403)
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def passenger_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") != "passenger":
                return error_response("Passenger privilege required", UNAUTHORIZED, status_code=403)
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def verified_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user_identity = get_jwt_identity()
            
            # Dynamically import User model to avoid circular imports during init
            try:
                from app.models.user import User  # Will fail if model doesn't exist yet, but expected to check DB
                user = User.query.get(user_identity)
                if not user or not user.is_verified:
                    return error_response("Email not verified", EMAIL_NOT_VERIFIED, status_code=403)
            except ImportError:
                # Fallback to claims if User model isn't built yet
                claims = get_jwt()
                if not claims.get("is_verified", False):
                    return error_response("Email not verified", EMAIL_NOT_VERIFIED, status_code=403)
                    
            return fn(*args, **kwargs)
        return decorator
    return wrapper
