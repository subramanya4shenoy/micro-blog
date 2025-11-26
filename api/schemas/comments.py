from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

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