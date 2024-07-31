from rest_marshmallow import Schema, fields

class FamilyMemberSchema(Schema):
    id = fields.Int()
    first_name = fields.Str()
    last_name = fields.Str()
    date_of_birth = fields.Date()
    gender = fields.Str()
    address = fields.Str()
    phone_number = fields.Str()
    email = fields.Email()
    occupation = fields.Str()

class FamilyTreeSchema(Schema):
    member = fields.Nested(FamilyMemberSchema)
    parents = fields.List(fields.Nested(FamilyMemberSchema))
    children = fields.List(fields.Nested(FamilyMemberSchema))
    spouses = fields.List(fields.Nested(FamilyMemberSchema))
