from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class IntentResult:
    intent: str
    argument: str | None = None
    task_id: int | None = None


ADD_TASK_RE = re.compile(r"^add\s+task\s+(.+)$", re.IGNORECASE)
COMPLETE_TASK_RE = re.compile(r"^complete\s+task\s+(\d+)$", re.IGNORECASE)
REMEMBER_RE = re.compile(r"^remember\s+(.+)$", re.IGNORECASE)
RECALL_RE = re.compile(r"^recall\s+(.+)$", re.IGNORECASE)
CREATE_NOTE_RE = re.compile(r"^create\s+note\s+(.+)$", re.IGNORECASE)


def classify_intent(message: str) -> IntentResult:
    text = message.strip()
    low = text.lower()

    match = ADD_TASK_RE.match(text)
    if match:
        return IntentResult(intent="add_task", argument=match.group(1).strip())

    if low == "list tasks":
        return IntentResult(intent="list_tasks")

    match = COMPLETE_TASK_RE.match(text)
    if match:
        return IntentResult(intent="complete_task", task_id=int(match.group(1)))

    match = REMEMBER_RE.match(text)
    if match:
        return IntentResult(intent="remember", argument=match.group(1).strip())

    match = RECALL_RE.match(text)
    if match:
        return IntentResult(intent="recall", argument=match.group(1).strip())

    match = CREATE_NOTE_RE.match(text)
    if match:
        return IntentResult(intent="create_note", argument=match.group(1).strip())

    if low == "list notes":
        return IntentResult(intent="list_notes")

    return IntentResult(intent="general_chat", argument=text)
