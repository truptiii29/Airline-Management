from flask import Blueprint, request
from app.services import admin_service
from app.utils.responses import success_response, error_response
from app.utils.decorators import admin_required
from app.utils.constants import INVALID_INPUT

admin_dashboard_bp = Blueprint('admin_dashboard_bp', __name__, url_prefix='/api/v1/admin')

@admin_dashboard_bp.route('/dashboard', methods=['GET'])
@admin_required()
def dashboard():
    try:
        stats = admin_service.get_dashboard_stats()
        return success_response("Dashboard stats retrieved", data=stats)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@admin_dashboard_bp.route('/reports/revenue', methods=['GET'])
@admin_required()
def revenue_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'day')
        
        if not start_date or not end_date:
            return error_response("start_date and end_date are required", INVALID_INPUT, status_code=400)
            
        report = admin_service.get_revenue_report(start_date, end_date, group_by)
        return success_response("Revenue report retrieved", data=report)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)

@admin_dashboard_bp.route('/reports/occupancy', methods=['GET'])
@admin_required()
def occupancy_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return error_response("start_date and end_date are required", INVALID_INPUT, status_code=400)
            
        report = admin_service.get_occupancy_report(start_date, end_date)
        return success_response("Occupancy report retrieved", data=report)
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
