from schemas.users import UserLogin, UserSignup
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt
from models import User
from auth import SECRET_KEY, ALGORITHM, hash_password
from database import get_db
import logging
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import hash_password, verify_password, create_access_token
import os

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = os.getenv("JWT_SECRET", "change_me_in_prod")
ALGORITHM = "HS256"

def get_user_by_identifier (db: Session, identifier: str) -> User | None:
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

def is_existing_user(db: Session, user: UserSignup) -> bool:
    return db.query(User).filter((User.username == user.username) | (User.email == user.email)).first() is not None

def signup_user(db: Session, user: UserSignup) -> User:    
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, user: OAuth2PasswordRequestForm) -> User:
    identifier = user.username
    password = user.password
    user = get_user_by_identifier(db, identifier)
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user