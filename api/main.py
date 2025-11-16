from fastapi import FastAPI, HTTPException, Query
from database import check_db_connection
import psycopg2
import os
from pydantic import BaseModel
from routers import posts, users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-health")
def db_health():
    try:
        check_db_connection()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

app.include_router(posts.router)
app.include_router(users.router)