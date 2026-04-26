from flask import Blueprint, request, jsonify
import time

payment_single_bp = Blueprint('payment_single_bp', __name__, url_prefix='/api/v1/payment')

@payment_single_bp.route('', methods=['POST'])
def process_payment():
    data = request.get_json() or {}
    payment_method = data.get('payment_method')
    upi_id = data.get('upi_id')
    amount = data.get('amount')

    if not payment_method or not amount:
        return jsonify({
            "success": False, 
            "error": "payment_method and amount are required"
        }), 400

    if payment_method.lower() == 'upi':
        if not upi_id or upi_id.strip() == '':
            return jsonify({
                "success": False, 
                "error": "UPI ID is required for UPI payments"
            }), 400

    return jsonify({
        "success": True,
        "message": "Payment successful",
        "data": {
            "transaction_id": f"MOCK_TXN_{int(time.time())}",
            "amount": amount,
            "payment_method": payment_method
        }
    }), 200
