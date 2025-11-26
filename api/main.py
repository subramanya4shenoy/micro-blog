from fastapi import FastAPI, Query, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from middleware.request_id import RequestIdMiddleware
from logging_config import get_logger, setup_logging
from database import check_db_connection
import psycopg2
import os
from pydantic import BaseModel
from routers import posts, users, comments
from fastapi.middleware.cors import CORSMiddleware
from errors import ErrorPayload, AppError

setup_logging()
logger = get_logger("main")

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(RequestIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.warning(f"App error at {request.url}: {exc.code} - {exc.message}")

    payload = ErrorPayload(
        code = exc.code,
        message=exc.message,
        details=exc.details or {}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": payload.model_dump()}
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
app.include_router(comments.router)