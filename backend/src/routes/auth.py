"""
Authentication endpoints for user signup and login.
Provides /api/auth/signup and /api/auth/login endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.jwt import create_jwt_token
from src.auth.password import hash_password, verify_password
from src.db import get_session
from src.exceptions import BadRequestException, ConflictException, UnauthorizedException
from src.models import User
from src.schemas.auth import AuthResponse, LoginRequest, SignupRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Create a new user account.

    Args:
        request: Signup request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token and user data

    Raises:
        400: Invalid email format or password too short
        409: Email already registered
    """
    # Check if email already exists
    result = await session.execute(
        select(User).where(User.email == request.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ConflictException(detail="Email already registered")

    # Hash password
    password_hash = hash_password(request.password)

    # Create new user
    new_user = User(
        email=request.email,
        password_hash=password_hash
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Generate JWT token
    token = create_jwt_token(new_user.id, new_user.email)

    # Return response
    return AuthResponse(
        token=token,
        user=UserResponse(id=new_user.id, email=new_user.email)
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate user and return JWT token.

    Args:
        request: Login request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token and user data

    Raises:
        400: Missing email or password
        401: Invalid email or password
    """
    # Find user by email
    result = await session.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Use generic message to prevent user enumeration
        raise UnauthorizedException(detail="Invalid email or password")

    # Verify password
    if not verify_password(request.password, user.password_hash):
        # Use same generic message as email-not-found case
        raise UnauthorizedException(detail="Invalid email or password")

    # Generate JWT token
    token = create_jwt_token(user.id, user.email)

    # Return response
    return AuthResponse(
        token=token,
        user=UserResponse(id=user.id, email=user.email)
    )
