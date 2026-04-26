from marshmallow import Schema, fields

class AirportNestedSchema(Schema):
    iata_code = fields.String()
    name = fields.String()
    city = fields.String()

class AircraftNestedSchema(Schema):
    model = fields.String()

class FlightCreateSchema(Schema):
    flight_number = fields.String(required=True)
    source_airport_id = fields.Integer(required=True)
    destination_airport_id = fields.Integer(required=True)
    aircraft_id = fields.Integer(required=True)
    departure_time = fields.DateTime(required=True)
    arrival_time = fields.DateTime(required=True)
    base_price_economy = fields.Decimal(required=True, as_string=True)
    base_price_business = fields.Decimal(required=True, as_string=True)
    base_price_first = fields.Decimal(required=True, as_string=True)

class FlightUpdateSchema(Schema):
    flight_number = fields.String(required=False)
    source_airport_id = fields.Integer(required=False)
    destination_airport_id = fields.Integer(required=False)
    aircraft_id = fields.Integer(required=False)
    departure_time = fields.DateTime(required=False)
    arrival_time = fields.DateTime(required=False)
    base_price_economy = fields.Decimal(required=False, as_string=True)
    base_price_business = fields.Decimal(required=False, as_string=True)
    base_price_first = fields.Decimal(required=False, as_string=True)

class FlightResponseSchema(Schema):
    id = fields.Integer()
    flight_number = fields.String()
    source_airport = fields.Nested(AirportNestedSchema)
    destination_airport = fields.Nested(AirportNestedSchema)
    aircraft = fields.Nested(AircraftNestedSchema)
    departure_time = fields.DateTime()
    arrival_time = fields.DateTime()
    duration_minutes = fields.Integer()
    
    duration_display = fields.Method("get_duration_display")
    
    def get_duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        return f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
