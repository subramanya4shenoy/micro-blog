from typing import Optional, Tuple, List
from models import Post #db 

from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from schemas.posts import PostCreate


def list_post(
    db: Session,
    *,
    page: int, 
    limit: int,
    search: Optional[str],
    sort_by: str,
    order: str,
    author_id: Optional[int]
) -> Tuple[List[Post], int]:
    offset = (page - 1) * limit
    query = db.query(Post)

    #filtering 
    if search:
        query = query.filter(
            or_(
                Post.title.ilike(f"%{search}%"),
                Post.content.ilike(f"%{search}%")
            )
        )

    if author_id is not None:
        query = query.filter(Post.user_id == author_id)
    
    #sorting
    sort_column = Post.title if sort_by == "title" else Post.created_at
    if order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total


def get_post(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()

def create_post(db: Session, *, user_id: int, data: PostCreate) -> Optional[Post]:
    new_post = Post(
        title=data.title,
        content=data.content,
        user_id=user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

def update_post(db: Session, *, post_id: int, data: PostCreate) -> Optional[Post]:
    post = get_post(db, post_id)
    if post is None:
        return None

    post.title = data.title
    post.content = data.content
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, *, post_id: int) -> bool:
    post = get_post(db, post_id)
    if post is None:
        return False

    db.delete(post)
    db.commit()
    return True