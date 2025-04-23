import psycopg2
import os
from contextlib import contextmanager
from datetime import datetime

DB_NAME = os.getenv("POSTGRES_DB", "yoloapp")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"

@contextmanager
def get_conn():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def create_tracking_table():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS object_tracking
                """);
            cur.execute("""
                CREATE TABLE IF NOT EXISTS object_tracking (
                    id SERIAL PRIMARY KEY,
                    track_id INTEGER NOT NULL UNIQUE,
                    entered_at TIMESTAMP NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    elapsed_time REAL NOT NULL
                );
            """)
