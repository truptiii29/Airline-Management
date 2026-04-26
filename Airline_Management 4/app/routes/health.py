from flask import Blueprint, jsonify
from datetime import datetime, timezone
from sqlalchemy import text
from app.extensions import db

health_bp = Blueprint('health_bp', __name__, url_prefix='/api/v1')

@health_bp.route('/health', methods=['GET'])
def health_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ok",
            "db": "connected",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception:
        return jsonify({
            "status": "error",
            "db": "disconnected",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500
