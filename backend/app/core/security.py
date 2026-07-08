from datetime import datetime, timedelta, UTC
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

# Importing your settings and custom exceptions
from app.core.config import get_settings
from app.core.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
)

from app.models.user_model import User

# Initialize Argon2 password hasher globally
argon2_ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash password using Argon2."""
    if len(password) > 128:
        # Prevent DoS attacks from massive inputs at the validation layer
        raise ValueError("Password exceeds maximum allowed length of 128 characters.")
    
    try:
        return argon2_ph.hash(password)
    except Exception as e:
        raise ValueError(f"Password hashing failed: {str(e)}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using Argon2."""
    try:
        argon2_ph.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, InvalidHash):
        return False
    except Exception:
        return False


def create_access_token(user: User) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.emp_id,          # use emp_id here
        "exp": expire,
        "type": "access",
        "user": {
            "id": str(user.id),
            "emp_id": user.emp_id,
            "email": user.email,
            "full_name": user.full_name,
            "is_first_login": user.is_first_login,
            "roles": [
                {
                    "id": str(role.id),
                    "name": role.name,
                    "description": role.description,
                }
                for role in user.roles
            ],
        },
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: str) -> str:
    """Create long-lived refresh token."""
    expire = datetime.now(UTC) + timedelta(
        days=get_settings().REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(
        payload,
        get_settings().JWT_SECRET_KEY.get_secret_value(),
        algorithm=get_settings().JWT_ALGORITHM,
    )


def _decode_token(token: str, expected_type: str) -> dict:
    """
    Base function to securely decode and validate JWTs.
    """
    try:
        payload = jwt.decode(
            token,
            get_settings().JWT_SECRET_KEY.get_secret_value(),
            algorithms=[get_settings().JWT_ALGORITHM],
        )
        
        # Verify the token is being used for its intended purpose
        if payload.get("type") != expected_type:
            # Raises your custom exception (no args needed)
            raise InvalidTokenException()
            
        return payload
        
    except ExpiredSignatureError:
        # Raises your custom exception (no args needed)
        raise TokenExpiredException()
    except (InvalidTokenError, InvalidTokenException):
        raise InvalidTokenException()
    except Exception:
        raise InvalidTokenException()


def decode_access_token(token: str) -> dict:
    """Decode access token with strict type validation."""
    return _decode_token(token, expected_type="access")


def decode_refresh_token(token: str) -> dict:
    """Decode refresh token with strict type validation."""
    return _decode_token(token, expected_type="refresh")