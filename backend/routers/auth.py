from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from backend.database import get_db
from backend import models
from backend import auth

router = APIRouter(prefix="/auth", tags=["Authentication"])

class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(models.User).filter(
        (models.User.email == data.email) | (models.User.username == data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    new_user = models.User(
        username=data.username,
        email=data.email,
        password_hash=auth.hash_password(data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create token
    token = auth.create_access_token({"user_id": new_user.id})
    
    return {
        "user_id": new_user.id,
        "username": new_user.username,
        "token": token
    }

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    
    if not user or not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    token = auth.create_access_token({"user_id": user.id})
    
    return {
        "user_id": user.id,
        "username": user.username,
        "token": token
    }
