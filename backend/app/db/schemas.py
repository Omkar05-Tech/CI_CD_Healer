# app/db/schemas.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class RunRequest(BaseModel):
    repo_url: str
    team_name: str
    leader_name: str
    github_token: str

class RunResponse(BaseModel):
    status: str
    iterations: int
    total_fixes: int
    time_taken: float


# -------------------------
# USER SCHEMAS
# -------------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    id: Optional[int] = None


# -------------------------
# EXTENDED TOKEN SCHEMA
# -------------------------
class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# -------------------------
# PASSWORD RESET SCHEMAS
# -------------------------
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str