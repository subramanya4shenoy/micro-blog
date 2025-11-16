
from pydantic import BaseModel
import psycopg2
import os
from fastapi import Query, HTTPException, APIRouter

class PostCreate(BaseModel):
    title: str
    content: str

router = APIRouter()

@router.get("/posts")
def list_post(page: int = Query(default=1, ge=1), 
              limit: int = Query(default=10, ge=0, le=100),
              query: str|None = Query(default=None, min_length=1)):
    # connect to postgress database using psycopg2
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    offset = (page - 1) * limit

    if query:
        cursor.execute("""SELECT id, title, content, created_at, updated_at 
                          FROM posts 
                          WHERE title ILIKE %s OR content ILIKE %s 
                          ORDER BY created_at DESC LIMIT %s OFFSET %s""",
                          (f"%{query}%",f"%{query}%", limit, offset), )
        rows = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM posts WHERE title ILIKE %s OR content ILIKE %s", (f"%{query}%",f"%{query}%",))
        total = cursor.fetchone()[0]
    else:
        cursor.execute("SELECT id, title, content, created_at, updated_at from posts ORDER BY created_at DESC LIMIT %s OFFSET %s", (limit, offset))
        rows = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM posts")
        total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "posts": [
        { "id": row[0], "title": row[1], "content": row[2], "created_at": row[3], "updated_at": row[4] } for row in rows
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/post/{post_id}")
def get_post(post_id: int):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, content, created_at, updated_at FROM posts WHERE id = %s",
        (post_id,),
    )
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "created_at": row[3],
        "updated_at": row[4]
    }
    
@router.post("/post")
def create_post(post: PostCreate):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute(
    """
    INSERT INTO posts (title, content)
    VALUES (%s, %s)
    RETURNING id, title, content, created_at, updated_at
    """,
    (post.title, post.content)
    )
    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return { "id": row[0], "title": row[1], "content": row[2], "created_at": row[3], "updated_at": row[4] }

@router.delete("/post/{post_id}")
def delete_post(post_id:int):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING id, title, content", (post_id,),)
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Post not found")

    conn.commit()
    cursor.close()
    conn.close()
    return { "id": row[0], "title": row[1], "content": row[2] }

@router.put("/post/{post_id}")
def update_post(post_id:int, post: PostCreate):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("UPDATE posts SET title = %s, content = %s WHERE id = %s RETURNING id, title, content", (post.title, post.content, post_id,),)
    row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Post not found")

    conn.commit()
    cursor.close()
    conn.close()