from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from middleware.request_id import RequestIdMiddleware
from logging_config import get_logger, setup_logging
from database import check_db_connection
from routers import posts, users, comments
from fastapi.middleware.cors import CORSMiddleware
from errors import ErrorPayload, AppError
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

import os

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

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up rate limiter")
    r = redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)
    logger.info("Rate limiter initialized")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down rate limiter")

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