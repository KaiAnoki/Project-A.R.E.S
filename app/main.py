from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from app.core.agent import process_message
from app.core.config import APP_DIR
from app.core.llm_local import OllamaError, list_local_models
from app.db.schema import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Project ARES", version="1.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)

    @field_validator("message")
    @classmethod
    def message_must_contain_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must contain text")
        return cleaned


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
def health() -> dict:
    init_db()
    try:
        models = list_local_models(timeout=2.0)
        return {"status": "ok", "ollama": "reachable", "models": models}
    except OllamaError as exc:
        return {"status": "degraded", "ollama": "unreachable", "detail": str(exc), "models": []}


@app.post("/chat")
def chat(payload: ChatIn) -> dict:
    return process_message(payload.message)
