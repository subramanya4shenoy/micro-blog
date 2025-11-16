import os
from fastapi import APIRouter, HTTPException, status
import psycopg2
from pydantic import BaseModel
from auth import hash_password, verify_password, create_access_token

class UserSignup(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str

router = APIRouter()

def get_db_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def _get_user_by_identifier (identifier: str):
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = %s OR email = %s", (identifier, identifier),)
    row = cursor.fetchone()

    cursor.close()
    conn.close()
    return row


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user: UserSignup):
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (user.username, user.username), )

    is_existing_user = cursor.fetchone()

    if is_existing_user:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exist")

    hashed_password = hash_password(user.password)

    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id, username, email", (user.username, user.email, hashed_password),)
    created_user = cursor.fetchone()

    conn.commit()
    
    cursor.close()
    conn.close()

    return UserOut(id=created_user[0], username=created_user[1], email=created_user[2])

@router.post("/login")
def login(credentials: UserLogin):
    row = _get_user_by_identifier(credentials.username_or_email)
    if row is None:
        raise HTTPException(detail="invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_id, username, email, password_hash = row

    if not verify_password(credentials.password, password_hash):
        raise HTTPException(detail="invalid credentials", status_code=status.HTTP_401_UNAUTHORIZED)
    
    access_token = create_access_token({"sub": str(user_id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user_id, "username": username, "email": email}
    }


