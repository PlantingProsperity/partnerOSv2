"""Security primitives for password hashing and token signing."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer


def hash_password(password: str, *, iterations: int = 390_000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{iterations}${base64.b64encode(salt).decode()}${base64.b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        iter_s, salt_b64, digest_b64 = encoded.split("$", maxsplit=2)
        iterations = int(iter_s)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
    except Exception:
        return False

    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(digest, expected)


def issue_token(secret: str, payload: dict[str, Any]) -> str:
    serializer = URLSafeTimedSerializer(secret_key=secret, salt="partner-os-v2-auth")
    return serializer.dumps(payload)


def verify_token(secret: str, token: str, max_age: int) -> dict[str, Any]:
    serializer = URLSafeTimedSerializer(secret_key=secret, salt="partner-os-v2-auth")
    try:
        data = serializer.loads(token, max_age=max_age)
    except SignatureExpired as exc:
        raise ValueError("Token expired") from exc
    except BadSignature as exc:
        raise ValueError("Invalid token") from exc

    if not isinstance(data, dict):
        raise ValueError("Invalid token payload")
    return data
