from marshmallow import Schema, fields

class SeatLockSchema(Schema):
    flight_id = fields.Integer(required=True)
    seat_number = fields.String(required=True)

class PassengerUpdateSchema(Schema):
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    phone = fields.String(required=False)
    address = fields.String(required=False)
    nationality = fields.String(required=False)
    date_of_birth = fields.Date(required=False)
