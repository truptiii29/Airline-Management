import os
import time
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from app.extensions import db, jwt, mail, cors, migrate, celery

def create_app(config_name=None):
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    if config_name == 'production':
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize celery config
    celery.conf.update(app.config)
    
    # JWT Blocklist checking
    from app.services.auth_service import check_if_token_revoked
    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        return check_if_token_revoked(jwt_header, jwt_payload)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.flights import flights_bp
    from app.routes.seat_map import seats_bp
    from app.routes.bookings import bookings_bp
    from app.routes.payments import payments_bp
    from app.routes.flight_status import flight_status_bp
    from app.routes.passengers import passengers_bp
    from app.routes.health import health_bp
    from app.routes.admin.dashboard import admin_dashboard_bp
    from app.routes.admin.flights import admin_flights_bp
    from app.routes.admin.bookings import admin_bookings_bp
    from app.routes.admin.passengers import admin_passengers_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(flights_bp)
    app.register_blueprint(seats_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(flight_status_bp)
    app.register_blueprint(passengers_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_flights_bp)
    app.register_blueprint(admin_bookings_bp)
    app.register_blueprint(admin_passengers_bp)

    @app.route('/api/v1/payment', methods=['POST'])
    def process_payment():
        print(request.json)
        data = request.json or {}
        payment_method = data.get('payment_method')
        upi_id = data.get('upi_id')
        amount = data.get('amount')

        if not payment_method or not amount:
            return jsonify({"success": False, "message": "Invalid input"}), 400

        if payment_method.lower() == 'upi' and not upi_id:
            return jsonify({"success": False, "message": "UPI ID is required"}), 400

        return jsonify({
            "success": True,
            "message": "Payment successful"
        }), 200

    # Logging configuration
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

    # Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({"success": False, "error": {"message": "Bad Request", "code": 400, "details": str(error)}}), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        return jsonify({"success": False, "error": {"message": "Unauthorized", "code": 401, "details": str(error)}}), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({"success": False, "error": {"message": "Forbidden", "code": 403, "details": str(error)}}), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"success": False, "error": {"message": "Not Found", "code": 404, "details": str(error)}}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"success": False, "error": {"message": "Internal Server Error", "code": 500, "details": str(error)}}), 500

    # Request Logging Middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if request.path == '/favicon.ico':
            return response
            
        latency_ms = int((time.time() - getattr(g, 'start_time', time.time())) * 1000)
        
        user_identity = None
        try:
            verify_jwt_in_request(optional=True)
            user_identity = get_jwt_identity()
        except Exception:
            pass

        app.logger.info(
            f"Method: {request.method} | URL: {request.url} | "
            f"User Identity: {user_identity} | "
            f"Status: {response.status_code} | Response Time: {latency_ms}ms"
        )
        return response

    from app.cli import register_cli_commands
    register_cli_commands(app)

    return app
