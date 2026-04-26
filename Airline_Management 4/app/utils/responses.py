from flask import jsonify

def success_response(message, data=None, status_code=200):
    response_body = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response_body), status_code

def error_response(message, code, details=None, status_code=400):
    response_body = {
        "success": False,
        "error": {
            "message": message,
            "code": code,
            "details": details
        }
    }
    return jsonify(response_body), status_code
