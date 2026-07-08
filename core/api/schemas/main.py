from datetime import datetime
from uuid import UUID

from ninja import Schema


class BaseServiceSchema(Schema):
    id: UUID
    created_at: datetime


class ServiceIncludeSchema(Schema):
    id: UUID
    name: str
    created_at: datetime


class ServiceListSchema(BaseServiceSchema):
    title: str
    name: str
    short_description: str
    price_from: str
    includes: list[ServiceIncludeSchema]


class ContactFormBaseSchema(Schema):
    name: str
    email: str
    message: str


class ContactFormSchema(ContactFormBaseSchema):
    id: UUID
    created_at: datetime


class ContactFormCreateSchema(ContactFormBaseSchema):
    pass
