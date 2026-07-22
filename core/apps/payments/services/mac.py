"""MAC (Message Authentication Code) helpers for the SQB E-commerce Service.

Per the SQB SES documentation ("Алгоритм создания MAC кода"): each field value is
prefixed with its own ASCII length, missing fields are represented by '-', all
fields are concatenated in a fixed order, and the result is signed with HMAC
(SHA1 by default). The exact field order per request type is agreed with the
bank separately, hence it lives next to each call site rather than here.
"""

import hashlib
import hmac


def _length_prefixed(value) -> str:
    if value is None or value == "":
        return "-"
    value = str(value)
    return f"{len(value)}{value}"


def build_signable_string(ordered_values: list) -> str:
    return "".join(_length_prefixed(value) for value in ordered_values)


def compute_mac(ordered_values: list, key_hex: str, algorithm: str = "sha1") -> str:
    key = bytes.fromhex(key_hex)
    message = build_signable_string(ordered_values).encode("utf-8")
    digest = hmac.new(key, message, getattr(hashlib, algorithm)).hexdigest()
    return digest.upper()


def verify_mac(
    ordered_values: list, key_hex: str, expected_mac: str, algorithm: str = "sha1"
) -> bool:
    computed = compute_mac(ordered_values, key_hex, algorithm)
    return hmac.compare_digest(computed.upper(), expected_mac.upper())
