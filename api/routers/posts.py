from datetime import datetime
from sqlalchemy import or_ 
from typing import Optional, List
from pydantic import BaseModel
from fastapi import Depends, Query, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from models import Post


from database import get_db

class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int

class PostOut(BaseModel):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    class Config:
        orm_mode = True


router = APIRouter(tags=["micro-posts"])

@router.get("/posts", response_model=List[PostOut])
def list_post(page: int = Query(default=1, ge=1), 
              limit: int = Query(default=10, ge=0, le=100),
              query: str|None = Query(default=None, min_length=1),
              db: Session = Depends(get_db),):

    offset = (page - 1) * limit
    posts_query = db.query(Post)
    if query:
        posts_query = posts_query.filter(
            or_(
                Post.title.ilike(f"%{query}%"),
                Post.content.ilike(f"%{query}%")
            )
        )
    posts = (
        posts_query
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return posts

@router.get("/post/{post_id}", response_model=PostOut)
def get_post(post_id: int,  db: Session = Depends(get_db),):
    post = (db.query(Post).filter((Post.id == post_id)).first())
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
    
@router.post("/post", response_model=PostOut)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(title = post.title, content = post.content, user_id = None);
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/post/{post_id}")
def delete_post(post_id:int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return None

@router.put("/post/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostCreate, db: Session = Depends(get_db)):
    existing = db.query(Post).filter(Post.id == post_id).first()
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    
    existing.title = payload.title
    existing.content = payload.content

    db.commit()
    db.refresh(existing)
    return existing
