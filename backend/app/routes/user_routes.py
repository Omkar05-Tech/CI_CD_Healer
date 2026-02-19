# app/routes/user_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# ✅ FIXED IMPORTS
from app.db.database import get_db
from app.db.models import User
from app.db.schemas import UserResponse, UserCreate, TokenData

from app.auth import hashing, oauth2

router = APIRouter(
    tags=["Users"]
)


# ---------------------------
# 👤 CREATE USER (REGISTER)
# ---------------------------
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {request.email} already exists."
        )

    new_user = User(
        email=request.email,
        hashed_password=hashing.Hash.bcrypt(request.password),
        full_name=request.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------------------
# 👤 GET CURRENT USER
# ---------------------------
@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(oauth2.get_current_user)
):
    user = db.query(User).filter(User.email == current_user.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ---------------------------
# 🔍 GET USER BY ID
# ---------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )

    return user


# ---------------------------
# 📊 GET ALL USERS
# ---------------------------
@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# ---------------------------
# ✏️ UPDATE CURRENT USER
# ---------------------------
@router.put("/me", response_model=UserResponse)
def update_current_user(
    update_data: dict,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(oauth2.get_current_user)
):
    user = db.query(User).filter(User.email == current_user.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only allow safe fields
    if "full_name" in update_data:
        user.full_name = update_data["full_name"]

    db.commit()
    db.refresh(user)

    return user
