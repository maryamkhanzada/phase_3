"""
Password hashing and verification using bcrypt.
Implements secure password storage with bcrypt hashing algorithm.
"""
from passlib.context import CryptContext


# Bcrypt context with cost factor 12 (recommended for security vs performance balance)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string suitable for storage

    Example:
        >>> password_hash = hash_password("securepassword123")
        >>> len(password_hash) > 50  # Bcrypt hashes are long
        True
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a stored hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored bcrypt hash

    Returns:
        True if password matches, False otherwise

    Example:
        >>> password_hash = hash_password("securepassword123")
        >>> verify_password("securepassword123", password_hash)
        True
        >>> verify_password("wrongpassword", password_hash)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)
