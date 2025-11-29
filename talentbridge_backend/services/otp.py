import random
import time
from typing import Dict, Tuple

# phone -> (otp, expiry_timestamp)
_otp_store: Dict[str, Tuple[str, float]] = {}


def generate_and_store_otp(phone: str, ttl_seconds: int = 300) -> str:
    otp = str(random.randint(100000, 999999))
    expiry = time.time() + ttl_seconds
    _otp_store[phone] = (otp, expiry)
    # TODO: in a real system, send this OTP via SMS/email provider
    print(f"[DEBUG] OTP for {phone}: {otp}")
    return otp


def verify_otp(phone: str, otp: str) -> bool:
    if phone not in _otp_store:
        return False
    stored_otp, expiry = _otp_store[phone]
    if time.time() > expiry:
        del _otp_store[phone]
        return False
    if stored_otp != otp:
        return False
    del _otp_store[phone]
    return True
