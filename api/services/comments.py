

from models import Comments, Post
from sqlalchemy.orm import Session

def list_comments(db: Session, post_id: int, page: int, limit: int):
    offset = (page -1) * limit    
    comments = db.query(Comments).filter(Comments.post_id == post_id)
    total = comments.count()
    if comments.count() == 0:
        return [], 0, False, False
    comments = comments.order_by(Comments.created_at.desc()).offset(offset).limit(limit).all()
    has_next = (page * limit) < total
    has_prev = page > 1
    return comments, total, has_next, has_prev

def create_comment(db: Session, post_id: int, content: str, user_id: int):
    post = db.query(Post).filter(Post.id == post_id)
    if post is None:
        raise "None"

    comment = Comments(post_id=post_id, content=content, user_id=user_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment