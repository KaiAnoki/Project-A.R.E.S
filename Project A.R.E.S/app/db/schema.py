from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from app.core.config import DB_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                source TEXT NOT NULL DEFAULT 'manual',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS optimizer_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_name TEXT NOT NULL,
                model_name TEXT NOT NULL,
                score REAL NOT NULL,
                latency_ms REAL,
                success INTEGER NOT NULL,
                request_type TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_memories_created_id ON memories(id DESC);
            CREATE INDEX IF NOT EXISTS idx_chats_created_id ON chats(id DESC);
            CREATE INDEX IF NOT EXISTS idx_optimizer_history_lookup
                ON optimizer_history(request_type, model_name, created_at DESC);
            """
        )
        columns = {row[1] for row in conn.execute('PRAGMA table_info(memories)').fetchall()}
        if 'source' not in columns:
            conn.execute("ALTER TABLE memories ADD COLUMN source TEXT NOT NULL DEFAULT 'manual'")
