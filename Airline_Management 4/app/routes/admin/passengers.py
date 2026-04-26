from flask import Blueprint, request
from app.models.passenger import Passenger
from app.models.user import User
from app.utils.responses import success_response, error_response
from app.utils.decorators import admin_required
from app.extensions import db

admin_passengers_bp = Blueprint('admin_passengers_bp', __name__, url_prefix='/api/v1/admin')

@admin_passengers_bp.route('/passengers', methods=['GET'])
@admin_required()
def list_passengers():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search')
        
        query = Passenger.query.join(User)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Passenger.first_name.ilike(search_term),
                    Passenger.last_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
            
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for p in pagination.items:
            items.append({
                "id": p.id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "email": p.user.email,
                "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
                "passport_number": p.passport_number,
                "nationality": p.nationality,
                "phone": p.phone,
                "created_at": p.created_at.isoformat() if p.created_at else None
            })
            
        return success_response("Passengers retrieved", data={
            "items": items,
            "total": pagination.total,
            "pages": pagination.pages,
            "current_page": pagination.page
        })
    except Exception as e:
        return error_response("Internal server error", "SERVER_ERROR", details=str(e), status_code=500)
