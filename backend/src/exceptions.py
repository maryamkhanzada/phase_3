"""
Custom HTTP exception classes for consistent error handling.
Provides semantic exceptions with appropriate status codes.
"""
from fastapi import HTTPException, status


class UnauthorizedException(HTTPException):
    """
    401 Unauthorized - Authentication required or token invalid.

    Usage:
        raise UnauthorizedException()
        raise UnauthorizedException(detail="Custom message")
    """

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ForbiddenException(HTTPException):
    """
    403 Forbidden - Valid authentication but insufficient permissions.

    Usage:
        raise ForbiddenException()
        raise ForbiddenException(detail="Access denied")
    """

    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(HTTPException):
    """
    404 Not Found - Resource does not exist.

    Usage:
        raise NotFoundException()
        raise NotFoundException(detail="Task not found")
    """

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(HTTPException):
    """
    409 Conflict - Resource already exists.

    Usage:
        raise ConflictException(detail="Email already registered")
    """

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class BadRequestException(HTTPException):
    """
    400 Bad Request - Invalid input or validation error.

    Usage:
        raise BadRequestException(detail="Title is required")
    """

    def __init__(self, detail: str = "Bad request"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
