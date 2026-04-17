from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.core.config import APP_DIR
from app.core.agent import process_message
from app.core.llm_local import OllamaError, list_local_models
from app.db.schema import init_db

app = FastAPI(title="Project ARES")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health() -> dict:
    init_db()
    try:
        models = list_local_models(timeout=2.0)
        return {"status": "ok", "ollama": "reachable", "models": models}
    except OllamaError as exc:
        return {"status": "degraded", "ollama": "unreachable", "detail": str(exc), "models": []}


@app.post("/chat")
def chat(payload: ChatIn):
    return process_message(payload.message)
