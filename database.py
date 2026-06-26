import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import DB_PATH

TZ = ZoneInfo("Asia/Shanghai")

def get_conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def now_text():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_state (
            user_id INTEGER PRIMARY KEY,
            paused INTEGER NOT NULL DEFAULT 0,
            note TEXT,
            updated_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            detail TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_message(user_id, role, content):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (int(user_id), role, content, now_text()),
    )
    conn.commit()
    conn.close()

def get_history(user_id, limit=20):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT role, content FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (int(user_id), int(limit)),
    )
    rows = c.fetchall()
    conn.close()
    rows.reverse()
    return rows

def clear_history(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE user_id=?", (int(user_id),))
    conn.commit()
    conn.close()

def set_paused(user_id, paused, note=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO user_state (user_id, paused, note, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET paused=excluded.paused, note=excluded.note, updated_at=excluded.updated_at
        """,
        (int(user_id), 1 if paused else 0, note, now_text()),
    )
    conn.commit()
    conn.close()

def is_paused(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT paused FROM user_state WHERE user_id=?", (int(user_id),))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == 1)

def add_log(user_id, action, detail=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO logs (user_id, action, detail, created_at) VALUES (?, ?, ?, ?)",
        (user_id, action, detail[:2000], now_text()),
    )
    conn.commit()
    conn.close()
