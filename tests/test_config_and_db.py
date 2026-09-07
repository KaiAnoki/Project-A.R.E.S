from pathlib import Path

from app.core import memory, tools
from app.core.config import APP_DIR, BASE_DIR, DB_PATH
from app.db import schema


def test_application_paths_exist() -> None:
    assert APP_DIR == BASE_DIR / "app"
    assert (APP_DIR / "static").is_dir()
    assert (APP_DIR / "templates").is_dir()
    assert isinstance(DB_PATH, Path)


def test_database_and_tool_flow(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "test.db")
    memory._invalidate_corpus_cache()
    schema.init_db()

    assert tools.add_task("Audit routing") == "Added task #1: Audit routing"
    assert "Audit routing" in tools.list_tasks()
    assert tools.complete_task(1) == "Completed task #1."

    assert tools.remember_note("Ollama runs locally") == "Saved memory #1."
    recalled = memory.recall("Where does Ollama run?")
    assert recalled[0]["content"] == "Ollama runs locally"


def test_connection_rolls_back_on_error(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "rollback.db")
    schema.init_db()
    try:
        with schema.get_conn() as conn:
            conn.execute("INSERT INTO tasks(title) VALUES(?)", ("should rollback",))
            raise RuntimeError("stop")
    except RuntimeError:
        pass
    with schema.get_conn() as conn:
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    assert count == 0
