import os
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
import logging
from fastapi.security import OAuth2PasswordRequestForm

from auth import hash_password, verify_password, create_access_token
from database import get_db
from models import User

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("JWT_SECRET", "change_me_in_prod")
ALGORITHM = "HS256"

logger = logging.getLogger(__name__)

def _get_user_by_identifier (db: Session, identifier: str) -> User | None:
    return (db.query(User).filter((User.username == identifier) | (User.email == identifier)).first())

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    logger.info("INFO: Incoming token:", token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("🔍 Decoded payload:", payload)
    except Exception as e:
        logger.error("ERROR: JWT decode error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    print("ERROR: Extracted user_id:", user_id)

    user = db.query(User).filter(User.id == user_id).first()
    logger.info("INFO: Loaded user from DB:", user)

    if user is None:
        logger.error("ERROR: User not found in DB")
        raise HTTPException(status_code=401, detail="User not found")

    return user

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup,  db: Session = Depends(get_db)):

    is_existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()

    if is_existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exist")
    
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserOut(id=new_user.id, username=new_user.username, email=new_user.email)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    identifier = form_data.username
    password = form_data.password

    user = _get_user_by_identifier(db, identifier)
    
    if user is None:
        raise HTTPException(status_code=401, detail="invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        },
    }
