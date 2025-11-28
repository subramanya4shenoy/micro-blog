from typing import Optional

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas.users import UserLogin, UserSignup
from auth import (
    SECRET_KEY,      # use the same as auth.py
    ALGORITHM,       # use the same as auth.py
    hash_password,
    verify_password,
    create_access_token,
)

logger = logging.getLogger(__name__)

# This matches the /login path in your router
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """
    Find user by username OR email.
    """
    return (
        db.query(User)
        .filter((User.username == identifier) | (User.email == identifier))
        .first()
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract current user from JWT Bearer token.
    Used as a dependency in protected routes.
    """
    logger.info("INFO: Incoming token: %s", token)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("INFO: Decoded JWT payload: %s", payload)
    except JWTError as e:
        logger.error("ERROR: JWT decode error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id = payload.get("sub")
    logger.info("INFO: Extracted user_id from token: %s", user_id)

    if user_id is None:
        logger.error("ERROR: No 'sub' claim in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    logger.info("INFO: Loaded user from DB: %s", user)

    if user is None:
        logger.error("ERROR: User not found in DB")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def is_existing_user(db: Session, user: UserSignup) -> bool:
    return (
        db.query(User)
        .filter((User.username == user.username) | (User.email == user.email))
        .first()
        is not None
    )


def signup_user(db: Session, user: UserSignup) -> User:
    hashed_password = hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, form_data: OAuth2PasswordRequestForm) -> Optional[User]:
    """
    Validate username/email + password. Return User if OK, else None.
    """
    identifier = form_data.username  # can be email or username
    password = form_data.password

    user = get_user_by_identifier(db, identifier)
    if user is None:
        logger.info("Login failed: user %s not found", identifier)
        return None

    if not verify_password(password, user.password_hash):
        logger.info("Login failed: invalid password for user %s", identifier)
        return None

    logger.info("Login successful for user %s", identifier)
    return user