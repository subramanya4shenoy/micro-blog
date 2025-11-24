from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from routers.users import get_current_user
from models import Comments, Post, User
from sqlalchemy.orm import Session

from database import get_db


class CommentOut(BaseModel):
    id: int
    post_id: int
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedComment(BaseModel):
    items: List[CommentOut]
    page: int
    limit: int
    total: int
    has_next: bool
    has_prev: bool

router = APIRouter(tags=["posts-comment"])

class CommentCreate(BaseModel):
    comment: str

@router.get("/post/{post_id}/comments", response_model=PaginatedComment)
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    
    offset = (page -1) * limit
    query = db.query(Comments).filter(Comments.post_id == post_id)

    total = query.count()

    comments = (
        query
        .order_by(Comments.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    has_next = (page * limit) < total
    has_prev = page > 1

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
    post = db.query(Post).filter(Post.id == post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    
    comment = Comments(
        post_id = post_id,
        content = payload.comment,
        user_id = current_user.id
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return comment