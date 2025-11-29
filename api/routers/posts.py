from typing import Literal, Optional
from fastapi import Depends, Query, HTTPException, APIRouter, status
from logging_config import get_logger
from sqlalchemy.orm import Session
from models import User
from services.users import get_current_user
from schemas.posts import PaginatedPosts, PostOut, PostCreate
from fastapi_limiter.depends import RateLimiter
from database import get_db
from services import posts as post_service

logger = get_logger("routers.posts")
router = APIRouter(tags=["micro-posts"])

@router.get("/posts", response_model=PaginatedPosts, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def list_post(
    page: int = Query(default=1, ge=1), 
    limit: int = Query(default=10, ge=1, le=100),
    search: str|None = Query(default=None),
    sort_by:Literal["created_at", "title"] = Query(default="created_at"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    author_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    items, total = post_service.list_post(
        db=db,
        page=page,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
        author_id=author_id,
    )

    has_next = (page * limit) < total
    has_prev = page > 1

    return PaginatedPosts(
        items=items,
        page=page,
        limit=limit,
        total=total,
        has_next=has_next,
        has_prev=has_prev,
    )
              


@router.get("/post/{post_id}", response_model=PostOut)
def get_post(post_id: int,  db: Session = Depends(get_db),):
    post = post_service.get_post(db, post_id=post_id)
    if post is None:
        logger.error("Post not found", extra={"event": "POST_NOT_FOUND", "post_id": post_id})
        raise HTTPException(status_code=404, detail="Post not found")
    return post
    
@router.post("/post", response_model=PostOut, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = post_service.create_post(
        db, user_id=current_user.id, data=post
    )
    return new_post

@router.delete("/post/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    ok = post_service.delete_post(db, post_id=post_id)
    if not ok:
        logger.warning(
            "Delete failed, post not found",
            extra={"post_id": post_id, "status_code": status.HTTP_404_NOT_FOUND},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    logger.info("Post deleted", extra={"post_id": post_id})
    return {"success": True}


@router.put("/post/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostCreate, db: Session = Depends(get_db)):
    updated = post_service.update_post(db, post_id=post_id, data=payload)
    if updated is None:
        logger.warning(
            "Update failed, post not found",
            extra={"post_id": post_id, "status_code": status.HTTP_404_NOT_FOUND},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    logger.info("Post updated", extra={"post_id": post_id})
    return updated
