import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings

_ENC_PREFIX = "enc::"


def _build_fernet() -> Fernet:
    raw_key = (settings.ENCRYPTION_KEY or settings.SECRET_KEY or "").encode("utf-8")
    digest = hashlib.sha256(raw_key).digest()
    fernet_key = base64.urlsafe_b64encode(digest)
    return Fernet(fernet_key)


def is_encrypted_value(value: Optional[str]) -> bool:
    return bool(value and value.startswith(_ENC_PREFIX))


def encrypt_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if is_encrypted_value(normalized):
        return normalized
    token = _build_fernet().encrypt(normalized.encode("utf-8")).decode("utf-8")
    return f"{_ENC_PREFIX}{token}"


def decrypt_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if not is_encrypted_value(normalized):
        return normalized
    token = normalized[len(_ENC_PREFIX) :]
    try:
        return _build_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None
