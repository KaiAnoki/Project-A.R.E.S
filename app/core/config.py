from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
APP_DIR = BASE_DIR / "app"

configured_db_path = Path(os.getenv("ARES_DB_PATH", "ares.db")).expanduser()
DB_PATH = configured_db_path if configured_db_path.is_absolute() else BASE_DIR / configured_db_path

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
ARES_APP_HOST = os.getenv("ARES_APP_HOST", "127.0.0.1")
ARES_APP_PORT = int(os.getenv("ARES_APP_PORT", "8000"))
ARES_DEFAULT_MODEL = os.getenv("ARES_DEFAULT_MODEL", "phi3:mini")
ARES_ENABLE_PRIVATE_OVERRIDES = os.getenv("ARES_ENABLE_PRIVATE_OVERRIDES", "false").lower() == "true"

DEFAULT_MODEL_CANDIDATES = list(dict.fromkeys([
    "llama3.1:8b",
    "qwen2.5:7b",
    "phi3:mini",
    ARES_DEFAULT_MODEL,
]))
