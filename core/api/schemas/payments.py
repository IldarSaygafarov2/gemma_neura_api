from datetime import datetime
from decimal import Decimal
from uuid import UUID

from ninja import Schema


class OrderCreateSchema(Schema):
    service_id: UUID | None = None
    amount: Decimal
    details: str
    email: str
    currency: str = "860"


class OrderSchema(Schema):
    id: UUID
    order_id: str
    amount: Decimal
    currency: str
    details: str
    email: str
    status: str
    payment_url: str | None
    created_at: datetime


class SQBWebhookSchema(Schema):
    message: str
    time_stamp: str
    order_details: str
    order_id: str
    payment_amount: Decimal
    transaction_id: str
    status: str
    P_SIGN: str
