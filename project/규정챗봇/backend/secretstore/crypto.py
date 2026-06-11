import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def _fernet() -> Fernet:
    source_key = settings.SECRET_ENCRYPTION_KEY or settings.SECRET_KEY
    digest = hashlib.sha256(source_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(plain_text: str) -> str:
    return _fernet().encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_secret(cipher_text: str) -> str:
    return _fernet().decrypt(cipher_text.encode("utf-8")).decode("utf-8")
