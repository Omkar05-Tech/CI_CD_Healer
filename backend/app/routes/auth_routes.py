# app/routes/auth_routes.py

import os
import uuid
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth

# ✅ FIXED IMPORTS
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import (
    TokenWithUser,
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest
)

from app.auth import hashing, token
from app.utils.email_otp import send_otp_email

router = APIRouter(
    tags=["Auth"]
)

# ---------------------------
# 🌐 Google OAuth Config
# ---------------------------
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


# ---------------------------
# 🔐 LOGIN
# ---------------------------
@router.post("/login", response_model=TokenWithUser)
def login(
    request: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.username).first()

    if not user or not hashing.Hash.verify(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # ✅ INCLUSION: Pass the user.id into the access token payload
    access_token = token.create_access_token(data={"sub": user.email, "id": user.id})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# ---------------------------
# 🌐 GOOGLE LOGIN
# ---------------------------
@router.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for('auth_google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="auth_google_callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        google_token = await oauth.google.authorize_access_token(request)
        user_info = google_token.get('userinfo')
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Google auth failed: {e}")

    user_email = user_info['email']

    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        user = User(
            email=user_email,
            full_name=user_info.get('name'),
            # Create a random password for OAuth users
            hashed_password=hashing.Hash.bcrypt(str(uuid.uuid4()))
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # ✅ FIXED: Changed "user_id" to "id" to match verify_token and TokenData schema
    app_jwt = token.create_access_token(
        data={"sub": user.email, "id": user.id} 
    )

    return HTMLResponse(f"""
        <script>
            window.opener.postMessage({{
                "token": "{app_jwt}",
                "user": {{
                    "id": {user.id},
                    "email": "{user.email}",
                    "full_name": "{user.full_name}"
                }}
            }}, "*");
            window.close();
        </script>
    """)


# ---------------------------
# 📧 FORGOT PASSWORD
# ---------------------------
@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Forgot password request for email: {request.email}")
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        # Security best practice: don't reveal if email exists
        return {"message": "If your email is registered, you will receive an OTP."}

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Save to DB with TZ-aware UTC time
    user.reset_token = otp
    user.reset_token_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    db.commit()

    # Print to terminal for immediate verification
    print(f"✅ TERMINAL LOG: OTP for {user.email} is {otp}")

    # Attempt to send email
    email_sent = send_otp_email(user.email, otp)
    if not email_sent:
        print(f"❌ ERROR: Failed to send email to {user.email}")
        # We don't necessarily want to crash here if the OTP is at least saved in DB for dev
    
    return {"message": "OTP sent successfully"}


# ---------------------------
# 🔍 VERIFY OTP
# ---------------------------
@router.post("/verify-otp")
def verify_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Verifying OTP {request.otp} for {request.email}")
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.reset_token != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Ensure current time is compared against TZ-aware expiry
    if not user.reset_token_expiry or user.reset_token_expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    return {"message": "OTP verified"}


# ---------------------------
# 🔄 RESET PASSWORD
# ---------------------------
@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.reset_token != request.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if user.reset_token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    user.hashed_password = hashing.Hash.bcrypt(request.new_password)
    user.reset_token = None
    user.reset_token_expiry = None

    db.commit()

    return {"message": "Password reset successful"}
