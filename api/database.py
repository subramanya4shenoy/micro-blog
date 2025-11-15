import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, future=True)

def check_db_connection():
    """Simple SELECT 1 to confirm DB is alive."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))