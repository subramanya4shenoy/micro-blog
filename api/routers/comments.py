from typing import List
from datetime import datetime
from logging_config import get_logger
from services import comments as comments_service
from schemas.comments import CommentOut, PaginatedComment, CommentCreate
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from services.users import get_current_user
from models import Comments, Post, User
from sqlalchemy.orm import Session

from database import get_db

logger = get_logger("routers.comments")
router = APIRouter(tags=["posts-comment"])

@router.get("/post/{post_id}/comments", response_model=PaginatedComment)
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):  
    comments, total, has_next, has_prev = comments_service.list_comments(db, post_id, page, limit)

    if comments is None:
        logger.error(f"Post not found: id={post_id}", extra={"event": "POST_NOT_FOUND", "post_id": post_id})
        raise HTTPException(status_code=404, detail=str(e))
        
    return PaginatedComment(
        items=comments,
        page=page,
        limit=limit,
        total=total,
        has_next=has_next,
        has_prev=has_prev
    )

@router.post("/post/{post_id}/comment", response_model=CommentOut)
def create_comment(
    post_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        comment = comments_service.create_comment(db, post_id, payload.content, current_user.id)
        logger.info("Comment added", extra={"post_id": post_id})
        return comment
    except Exception as e:
        logger.error(f"Post not found: id={post_id}", extra={"event": "POST_NOT_FOUND", "post_id": post_id})
        raise HTTPException(status_code=404, detail=str(e))