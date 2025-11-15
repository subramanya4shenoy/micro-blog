from fastapi import FastAPI
from database import check_db_connection
import psycopg2
import os
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: str

app = FastAPI()

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

@app.get("/posts")
def list_post():
    # connect to postgress database using psycopg2
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, content, created_at, updated_at FROM posts ORDER BY created_at DESC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        { "id": row[0], "title": row[1], "content": row[2], "created_at": row[3], "updated_at": row[4] } for row in rows
    ]

@app.get("/post/{post_id}")
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
    
@app.post("/post")
def create_post(post: PostCreate):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO posts (title, content) 
    VALUES (%s, %s) 
    RETURNING id, title, content, created_at, updated_at", 
    (post.title, post.content, ),
    """)
    row = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return { "id": row[0], "title": row[1], "content": row[2], "created_at": row[3], "updated_at": row[4] }

@app.delete("/post/{post_id}")
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

@app.put("/post/{post_id}")
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
    return { "id": row[0], "title": row[1], "content": row[2] }