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

# def create_tracking_table():
#     with get_conn() as conn:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 DROP TABLE IF EXISTS object_tracking
#                 """);
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS object_tracking (
#                     id SERIAL PRIMARY KEY,
#                     track_id INTEGER NOT NULL UNIQUE,
#                     entered_at TIMESTAMP NOT NULL,
#                     last_seen TIMESTAMP NOT NULL,
#                     elapsed_time REAL NOT NULL
#                 );
#             """)

def insert_tracking_record(track_id: int, entered_at: float, last_seen: float):
    entered_dt = datetime.fromtimestamp(entered_at)
    last_seen_dt = datetime.fromtimestamp(last_seen)
    elapsed = round(last_seen - entered_at, 2)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO object_tracking (track_id, entered_at, last_seen, elapsed_time)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (track_id) DO UPDATE
                SET last_seen = EXCLUDED.last_seen,
                    elapsed_time = EXCLUDED.elapsed_time;
            """, (track_id, entered_dt, last_seen_dt, elapsed))
