from django.contrib import admin
from unfold import admin as unfold_admin

from .models import Order, Transaction


class TransactionInline(unfold_admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ["transaction_id", "amount", "status", "raw_payload", "created_at"]


@admin.register(Order)
class OrderAdmin(unfold_admin.ModelAdmin):
    list_display = ["order_id", "amount", "currency", "status", "email", "created_at"]
    list_filter = ["status", "currency"]
    search_fields = ["order_id", "email", "claim_id"]
    readonly_fields = ["order_id", "nonce", "claim_id", "payment_url"]
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(unfold_admin.ModelAdmin):
    list_display = ["transaction_id", "order", "amount", "status", "created_at"]
    search_fields = ["transaction_id", "order__order_id"]
