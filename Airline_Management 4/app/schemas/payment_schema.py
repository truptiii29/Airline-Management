from marshmallow import Schema, fields, validate

class PaymentInitiateSchema(Schema):
    booking_id = fields.Integer(required=True)
    payment_method = fields.String(required=True, validate=validate.OneOf(['upi', 'credit_card', 'debit_card', 'net_banking', 'cash']))

class PaymentResponseSchema(Schema):
    id = fields.Integer()
    transaction_id = fields.String()
    amount = fields.Decimal(as_string=True)
    payment_method = fields.String(attribute="payment_method.value")
    payment_status = fields.String(attribute="payment_status.value")
    payment_date = fields.DateTime()
    refund_amount = fields.Decimal(as_string=True)
    refund_date = fields.DateTime()
    gateway_response = fields.Dict()
