import time
import json
import base64
import hmac
import hashlib
from typing import Dict, Any, Optional
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger("security.jwt")

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def base64url_decode(data_str: str) -> bytes:
    padding = "=" * (4 - (len(data_str) % 4))
    return base64.urlsafe_b64decode(data_str + padding)

def create_access_token(subject: str, role: str = "admin", expires_in_seconds: Optional[int] = None) -> str:
    """Creates a signed JWT Access Token using HMAC-SHA256."""
    if expires_in_seconds is None:
        expires_in_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + expires_in_seconds,
    }

    encoded_header = base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

    signature = hmac.new(settings.JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def create_refresh_token(subject: str) -> str:
    """Creates a signed JWT Refresh Token with longer expiration (7 days)."""
    expires_in_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": now,
        "exp": now + expires_in_seconds,
    }

    encoded_header = base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")

    signature = hmac.new(settings.JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    encoded_signature = base64url_encode(signature)

    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def decode_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT signature and expiration timestamp."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed JWT token format")

        encoded_header, encoded_payload, encoded_signature = parts
        signing_input = f"{encoded_header}.{encoded_payload}".encode("utf-8")
        expected_sig = hmac.new(settings.JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
        provided_sig = base64url_decode(encoded_signature)

        if not hmac.compare_digest(expected_sig, provided_sig):
            raise ValueError("Invalid JWT signature")

        payload = json.loads(base64url_decode(encoded_payload).decode("utf-8"))
        if payload.get("exp") and time.time() > payload["exp"]:
            raise ValueError("JWT token has expired")

        return payload
    except Exception as err:
        logger.warning(f"JWT Token validation failed: {err}")
        raise ValueError(f"Invalid authentication token: {err}")
