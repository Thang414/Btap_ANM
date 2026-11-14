# Payment Gateway Microservice Core Module
import hmac
import hashlib
import time

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def process_transaction(order_id: str, amount_cents: int) -> dict:
    return {"status": "SUCCESS", "tx_id": f"tx_{int(time.time())}_{order_id}"}
