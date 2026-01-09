"""
JWT token verification and authentication dependencies.
Implements JWT validation using PyJWT with HS256 algorithm.
"""
from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import UUID

import jwt
from fastapi import Depends, Header

from src.config import settings
from src.exceptions import UnauthorizedException


def create_jwt_token(user_id: UUID, email: str) -> str:
    """
    Create a JWT token for a user.

    Args:
        user_id: User's UUID
        email: User's email address

    Returns:
        Signed JWT token string

    Example:
        >>> token = create_jwt_token(UUID("550e8400-e29b-41d4-a716-446655440000"), "user@example.com")
        >>> len(token) > 100  # JWT tokens are long
        True
    """
    expiration = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expiration_hours)

    payload = {
        "user_id": str(user_id),
        "email": email,
        "exp": expiration,
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm="HS256"
    )

    return token


def verify_jwt_token(token: str) -> Dict[str, str]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload containing user_id and email

    Raises:
        UnauthorizedException: If token is invalid, expired, or malformed

    Example:
        >>> token = create_jwt_token(UUID("550e8400-e29b-41d4-a716-446655440000"), "user@example.com")
        >>> payload = verify_jwt_token(token)
        >>> "user_id" in payload
        True
    """
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(detail="Token has expired")

    except jwt.InvalidTokenError:
        raise UnauthorizedException(detail="Invalid token")

    except Exception:
        raise UnauthorizedException(detail="Authentication failed")


async def get_current_user(authorization: str = Header(None)) -> str:
    """
    FastAPI dependency that extracts and validates JWT token from Authorization header.

    Args:
        authorization: Authorization header value (format: "Bearer <token>")

    Returns:
        user_id extracted from validated JWT token

    Raises:
        UnauthorizedException: If authorization header is missing, malformed, or token is invalid

    Usage:
        @router.get("/protected")
        async def protected_endpoint(current_user_id: str = Depends(get_current_user)):
            # current_user_id is guaranteed to be from a validated JWT
            return {"user_id": current_user_id}

    Example:
        >>> # In FastAPI endpoint
        >>> current_user_id = await get_current_user("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI...")
        >>> isinstance(current_user_id, str)
        True
    """
    if not authorization:
        raise UnauthorizedException(detail="Authorization header missing")

    # Extract token from "Bearer <token>" format
    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedException(detail="Invalid authorization header format. Expected: Bearer <token>")

    token = parts[1]

    # Verify token and extract user_id
    payload = verify_jwt_token(token)

    user_id = payload.get("user_id")
    if not user_id:
        raise UnauthorizedException(detail="Token payload missing user_id")

    return user_id
