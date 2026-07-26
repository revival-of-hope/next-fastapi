from datetime import timedelta
from typing import Any
from datetime import datetime, UTC
import jwt

from pwdlib import PasswordHash
from app.api.deps import ALGORITHM
from app.core.config import settings

hash_method = PasswordHash.recommended()


def create_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire_date = datetime.now(UTC) + expires_delta
    encode_content = {"exp": expire_date, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        encode_content,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return hash_method.verify(plain_password, hashed_password)


def hashing_password(plain_password: str) -> str:
    return hash_method.hash(plain_password)
