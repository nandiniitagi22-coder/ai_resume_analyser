import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, Any, List, Tuple, Optional

try:
    import pymysql  # optional for MySQL
except Exception:
    pymysql = None

DB_PATH = os.environ.get("SQLITE_PATH", os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")

def _ensure_sqlite_dir():
    os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

def using_mysql() -> bool:
    return bool(DB_HOST and DB_USER and DB_NAME)

@contextmanager
def get_conn():
    if using_mysql() and pymysql is not None:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD or "", database=DB_NAME, autocommit=True)
        try:
            yield conn
        finally:
            conn.close()
    else:
        _ensure_sqlite_dir()
        conn = sqlite3.connect(DB_PATH)
        try:
            yield conn
        finally:
            conn.commit()
            conn.close()

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                resume_score INTEGER,
                timestamp TEXT,
                page_no TEXT,
                predicted_field TEXT,
                user_level TEXT,
                actual_skills TEXT,
                recommended_skills TEXT,
                recommended_courses TEXT
            );"""
        )

def insert_user_record(record: Dict[str, Any]):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO user_data
            (name, email, resume_score, timestamp, page_no, predicted_field, user_level,
             actual_skills, recommended_skills, recommended_courses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""" if conn.__class__.__module__.startswith("sqlite3") else
            """INSERT INTO user_data
            (name, email, resume_score, timestamp, page_no, predicted_field, user_level,
             actual_skills, recommended_skills, recommended_courses)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                record.get("name",""), record.get("email",""), int(record.get("resume_score",0)),
                record.get("timestamp",""), record.get("page_no","1"), record.get("predicted_field",""),
                record.get("user_level",""), record.get("actual_skills",""), record.get("recommended_skills",""),
                record.get("recommended_courses",""),
            )
        )

def fetch_user_data() -> List[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, resume_score, timestamp, page_no, predicted_field, user_level FROM user_data ORDER BY id DESC;")
        return cur.fetchall()

def fetch_user_full(id_: int) -> Optional[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_data WHERE id = ?" if conn.__class__.__module__.startswith("sqlite3") else "SELECT * FROM user_data WHERE id = %s", (id_,))
        return cur.fetchone()
