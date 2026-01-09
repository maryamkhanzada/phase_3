"""
Authentication request and response schemas.
Defines Pydantic models for signup, login, and auth responses.
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class LoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User data in responses (excludes password_hash)."""

    id: UUID = Field(..., description="User UUID")
    email: str = Field(..., description="User email address")

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility


class AuthResponse(BaseModel):
    """Authentication response with token and user data."""

    token: str = Field(..., description="JWT access token")
    user: UserResponse = Field(..., description="User details")
