from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class PostCreate(BaseModel):
    title: str
    content: str

class PostOut(BaseModel):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    title: str
    content: str
    likes: int
    model_config = ConfigDict(from_attributes=True)

class PaginatedPosts(BaseModel):
    items: List[PostOut]
    page: int
    limit: int
    total: int
    has_next: bool
    has_prev: bool

class CommentCreate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
