from marshmallow import Schema, fields, validate

class BookingCreateSchema(Schema):
    flight_id = fields.Integer(required=True)
    seat_number = fields.String(required=True)
    seat_class = fields.String(required=True, validate=validate.OneOf(['economy', 'business', 'first']))

class FlightSimpleSchema(Schema):
    flight_number = fields.String()
    departure_time = fields.DateTime()

class PaymentSimpleSchema(Schema):
    payment_status = fields.String(attribute="payment_status.value")
    amount = fields.Decimal(as_string=True)

class BookingResponseSchema(Schema):
    id = fields.Integer()
    booking_reference = fields.String()
    seat_number = fields.String()
    seat_class = fields.String(attribute="seat_class.value")
    status = fields.String(attribute="status.value")
    total_amount = fields.Decimal(as_string=True)
    booking_date = fields.DateTime()
    flight_details = fields.Nested(FlightSimpleSchema)
    payment = fields.Nested(PaymentSimpleSchema)
