import secrets

from django.db import models, transaction

from core.apps.common.models import BaseModel
from core.apps.main.models import Service
from core.project import settings


class OrderSequence(models.Model):
    """Singleton row used to hand out gapless, ever-increasing numbers for order_id."""

    last_value = models.PositiveBigIntegerField(default=0)

    @classmethod
    def next_value(cls) -> int:
        with transaction.atomic():
            seq, _ = cls.objects.select_for_update().get_or_create(pk=1)
            seq.last_value += 1
            seq.save(update_fields=["last_value"])
            return seq.last_value


class Order(BaseModel):
    class Status(models.TextChoices):
        CREATED = "created", "Создан"
        AWAITING_PAYMENT = "awaiting_payment", "Ожидает оплаты"
        COMPLETED = "completed", "Оплачен"
        FAILED = "failed", "Ошибка оплаты"
        BLOCKED = "blocked", "Заблокирован"

    # SQB order_id: SQB_TERMINAL_ID (numeric part) + 6-digit zero-padded sequence number.
    order_id = models.CharField(max_length=12, unique=True, editable=False)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Услуга",
    )
    amount = models.DecimalField(verbose_name="Сумма", max_digits=12, decimal_places=2)
    currency = models.CharField(verbose_name="Код валюты", max_length=3, default="860")
    details = models.CharField(verbose_name="Детали оплаты", max_length=255)
    email = models.EmailField(verbose_name="Почта клиента")
    nonce = models.CharField(max_length=32, editable=False)
    claim_id = models.CharField(max_length=64, null=True, blank=True)
    payment_url = models.URLField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.CREATED
    )

    def save(self, *args, **kwargs):
        if not self.order_id:
            sequence = OrderSequence.next_value()
            self.order_id = f"{settings.SQB_TERMINAL_ID}{sequence:06d}"
        if not self.nonce:
            self.nonce = secrets.token_hex(16)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class Transaction(BaseModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_id = models.CharField(max_length=64)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)
    raw_payload = models.JSONField()

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"
