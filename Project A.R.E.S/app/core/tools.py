from __future__ import annotations

from app.core import memory
from app.db.schema import get_conn


def add_task(title: str) -> str:
    clean = title.strip()
    if not clean:
        return 'Task title was empty.'
    with get_conn() as conn:
        cur = conn.execute('INSERT INTO tasks(title) VALUES(?)', (clean,))
        task_id = int(cur.lastrowid)
    return f'Added task #{task_id}: {clean}'


def list_tasks() -> str:
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT id, title, status FROM tasks ORDER BY id DESC LIMIT 20'
        ).fetchall()
    if not rows:
        return 'No tasks found.'
    return '\n'.join([f"#{row['id']} [{row['status']}] {row['title']}" for row in rows])


def complete_task(task_id: int) -> str:
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE tasks SET status='done', completed_at=CURRENT_TIMESTAMP WHERE id=? AND status!='done'",
            (int(task_id),),
        )
    if cur.rowcount == 0:
        return f'Task #{task_id} was not found or is already done.'
    return f'Completed task #{task_id}.'


def create_note(content: str) -> str:
    clean = content.strip()
    if not clean:
        return 'Note content was empty.'
    with get_conn() as conn:
        cur = conn.execute('INSERT INTO notes(content) VALUES(?)', (clean,))
        note_id = int(cur.lastrowid)
    return f'Created note #{note_id}.'


def list_notes() -> str:
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT id, content, created_at FROM notes ORDER BY id DESC LIMIT 20'
        ).fetchall()
    if not rows:
        return 'No notes found.'
    return '\n'.join([f"#{row['id']} {row['content']}" for row in rows])


def remember_note(content: str) -> str:
    clean = content.strip()
    if not clean:
        return 'Memory content was empty.'
    mem_id = memory.remember(clean, source='manual')
    return f'Saved memory #{mem_id}.'


def recall_memory(query: str) -> str:
    clean = query.strip()
    if not clean:
        return 'Recall query was empty.'
    matches = memory.recall(clean)
    if not matches:
        return 'No matching memories found.'
    return '\n'.join([
        f"#{m['id']} (score={m['score']}, source={m['source']}) {m['content']}" for m in matches
    ])
