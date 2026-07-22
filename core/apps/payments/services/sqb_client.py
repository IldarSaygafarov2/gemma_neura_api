from datetime import datetime, timezone

import redis
import requests

from core.project import settings

from .mac import compute_mac

# Field order used to build the P_SIGN for "Получение Payment form URL" (Табл.3).
# TODO: confirm this order with SQB before going live - the documentation states
# it is agreed per-merchant with the bank's technical team.
PAYMENT_FORM_MAC_FIELDS = [
    "order_id",
    "amount",
    "details",
    "currency",
    "email",
    "country",
    "timestamp",
    "time_gmt",
    "trtype",
    "nonce",
    "language",
]

# Field order used to verify the P_SIGN on incoming webhook notifications (Табл.5).
# TODO: confirm this order with SQB before going live, same caveat as above.
WEBHOOK_MAC_FIELDS = [
    "message",
    "time_stamp",
    "order_details",
    "order_id",
    "payment_amount",
    "transaction_id",
    "status",
]

ACCESS_TOKEN_TTL_SECONDS = 5 * 60 - 10
REFRESH_TOKEN_TTL_SECONDS = 24 * 60 * 60 - 60

_REDIS_ACCESS_KEY = "sqb:access_token"
_REDIS_REFRESH_KEY = "sqb:refresh_token"


class SQBAPIError(Exception):
    def __init__(self, error_code, error_message):
        self.error_code = error_code
        self.error_message = error_message
        super().__init__(f"[{error_code}] {error_message}")


class SQBClient:
    def __init__(self):
        self.base_url = settings.SQB_BASE_URL.rstrip("/")
        self.username = settings.SQB_USERNAME
        self.password = settings.SQB_PASSWORD
        self.mac_key = settings.SQB_MAC_KEY
        self._redis = redis.from_url(settings.CELERY_BROKER_URL, decode_responses=True)

    def _raise_for_error(self, data: dict):
        if data.get("success") is False:
            raise SQBAPIError(data.get("error_code"), data.get("error_message"))

    def _fetch_token(self) -> str:
        response = requests.post(
            f"{self.base_url}/api/token/",
            json={"username": self.username, "password": self.password},
            timeout=10,
        )
        data = response.json()
        self._raise_for_error(data)
        self._redis.set(_REDIS_ACCESS_KEY, data["access"], ex=ACCESS_TOKEN_TTL_SECONDS)
        self._redis.set(_REDIS_REFRESH_KEY, data["refresh"], ex=REFRESH_TOKEN_TTL_SECONDS)
        return data["access"]

    def _refresh_access_token(self, refresh_token: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/token/refresh/",
            json={"refresh": refresh_token},
            timeout=10,
        )
        data = response.json()
        self._raise_for_error(data)
        self._redis.set(_REDIS_ACCESS_KEY, data["access"], ex=ACCESS_TOKEN_TTL_SECONDS)
        return data["access"]

    def get_access_token(self) -> str:
        access_token = self._redis.get(_REDIS_ACCESS_KEY)
        if access_token:
            return access_token

        refresh_token = self._redis.get(_REDIS_REFRESH_KEY)
        if refresh_token:
            return self._refresh_access_token(refresh_token)

        return self._fetch_token()

    def get_payment_form_url(self, order) -> dict:
        now = datetime.now(timezone.utc)
        body = {
            "order_id": order.order_id,
            "amount": int(order.amount),
            "details": order.details,
            "currency": order.currency,
            "email": order.email,
            "country": "UZ",
            "timestamp": now.strftime("%Y%m%d%H%M%S"),
            "time_gmt": "+5:00",
            "trtype": "1",
            "nonce": order.nonce,
            "language": "ru",
        }
        body["P_SIGN"] = compute_mac(
            [body[field] for field in PAYMENT_FORM_MAC_FIELDS], self.mac_key
        )

        response = requests.post(
            f"{self.base_url}/way4/get/url-link",
            json=body,
            headers={"Authorization": f"Bearer {self.get_access_token()}"},
            timeout=10,
        )
        data = response.json()
        self._raise_for_error(data)
        return data

    def get_transaction_history(self, code: str, **extra) -> dict:
        response = requests.post(
            f"{self.base_url}/api/get/transaction/history",
            json={"code": code, **extra},
            headers={"Authorization": f"Bearer {self.get_access_token()}"},
            timeout=10,
        )
        data = response.json()
        self._raise_for_error(data)
        return data
