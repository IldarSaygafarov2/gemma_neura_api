from ninja import Router
from ninja.errors import HttpError

from core.api.schemas.payments import OrderCreateSchema, OrderSchema, SQBWebhookSchema
from core.apps.payments.models import Order, Transaction
from core.apps.payments.services.mac import verify_mac
from core.apps.payments.services.sqb_client import (
    SQBAPIError,
    SQBClient,
    WEBHOOK_MAC_FIELDS,
)
from core.project import settings

router = Router(tags=["Payments"])


@router.post("/create", response=OrderSchema)
def create_payment(request, data: OrderCreateSchema):
    order = Order.objects.create(
        service_id=data.service_id,
        amount=data.amount,
        currency=data.currency,
        details=data.details,
        email=data.email,
    )

    try:
        result = SQBClient().get_payment_form_url(order)
    except SQBAPIError as exc:
        order.status = Order.Status.FAILED
        order.save(update_fields=["status"])
        raise HttpError(502, exc.error_message) from exc

    order.claim_id = result["claim_id"]
    order.payment_url = result["url"]
    order.status = Order.Status.AWAITING_PAYMENT
    order.save(update_fields=["claim_id", "payment_url", "status"])
    return order


@router.post("/webhook")
def sqb_webhook(request, data: SQBWebhookSchema):
    ordered_values = [getattr(data, field) for field in WEBHOOK_MAC_FIELDS]
    if not verify_mac(ordered_values, settings.SQB_MAC_KEY, data.P_SIGN):
        raise HttpError(403, "Invalid P_SIGN")

    try:
        order = Order.objects.get(order_id=data.order_id)
    except Order.DoesNotExist:
        raise HttpError(404, "Unknown order_id")

    Transaction.objects.create(
        order=order,
        transaction_id=data.transaction_id,
        amount=data.payment_amount,
        status=data.status,
        raw_payload=data.dict(),
    )

    order.status = (
        Order.Status.COMPLETED if data.status == "Completed" else Order.Status.FAILED
    )
    order.save(update_fields=["status"])

    return {"success": True}
