from ninja import Schema
from uuid import UUID
from datetime import datetime


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
