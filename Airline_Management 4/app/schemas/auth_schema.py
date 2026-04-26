from marshmallow import Schema, fields, validate

class AuthRegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    phone = fields.String(required=False)
    passport_number = fields.String(required=False)
    nationality = fields.String(required=False)
    date_of_birth = fields.Date(required=False)

class AuthLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)

class OTPVerifySchema(Schema):
    user_id = fields.Integer(required=True)
    otp_code = fields.String(required=True, validate=validate.Length(equal=6))
    purpose = fields.String(required=False)

class PasswordResetSchema(Schema):
    user_id = fields.Integer(required=True)
    otp_code = fields.String(required=True, validate=validate.Length(equal=6))
    new_password = fields.String(required=True, validate=validate.Length(min=8))
