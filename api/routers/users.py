import os
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

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


def _get_user_by_identifier (db: Session, identifier: str) -> User | None:
    return (db.query(User).filter((User.username == identifier) | (User.email == identifier)).first())


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
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = _get_user_by_identifier(db, credentials.username_or_email)
    if user is None:
        raise HTTPException(detail="invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED)
    
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(detail="invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "email": user.email}
    }


