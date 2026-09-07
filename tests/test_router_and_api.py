import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.llm_local import OllamaError
from app.core.router import classify_intent
from app.main import ChatIn, app


@pytest.mark.parametrize(("message", "intent"), [
    ("add task review logs", "add_task"),
    ("list tasks", "list_tasks"),
    ("complete task 12", "complete_task"),
    ("remember deployments keep account data", "remember"),
    ("recall account data", "recall"),
    ("create note check health", "create_note"),
    ("list notes", "list_notes"),
    ("explain the architecture", "general_chat"),
])
def test_command_routing(message: str, intent: str) -> None:
    assert classify_intent(message).intent == intent


def test_whitespace_chat_is_rejected() -> None:
    with pytest.raises(ValidationError, match="message must contain text"):
        ChatIn(message="   ")


def test_health_reports_degraded_without_ollama(monkeypatch, tmp_path) -> None:
    from app import main
    from app.db import schema

    monkeypatch.setattr(schema, "DB_PATH", tmp_path / "health.db")

    def unavailable(timeout: float) -> list[str]:
        raise OllamaError("Ollama unavailable")

    monkeypatch.setattr(main, "list_local_models", unavailable)
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
