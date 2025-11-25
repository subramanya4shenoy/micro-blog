import os
from schemas.users import UserSignup, UserOut
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from auth import hash_password, verify_password, create_access_token
from database import get_db
from models import User
from services.users import get_user_by_identifier, is_existing_user, login_user, signup_user, get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup,  db: Session = Depends(get_db)):
    existing_user = is_existing_user(db, user)
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exist")
    new_user = signup_user(db, user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = login_user(db, form_data)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid credentials")
    return user
