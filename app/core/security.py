
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password cannot exceed 72 UTF-8 bytes")

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify a password against its stored bcrypt hash."""

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """Create a signed JWT access token."""

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
