from __future__ import annotations

import os
from pathlib import Path

OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434').rstrip('/')
ARES_APP_HOST = os.getenv('ARES_APP_HOST', '127.0.0.1')
ARES_APP_PORT = int(os.getenv('ARES_APP_PORT', '8000'))
ARES_DEFAULT_MODEL = os.getenv('ARES_DEFAULT_MODEL', 'phi3:mini')
ARES_ENABLE_PRIVATE_OVERRIDES = os.getenv('ARES_ENABLE_PRIVATE_OVERRIDES', 'true').lower() == 'true'
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_CANDIDATES = [
    'llama3.1:8b',
    'qwen2.5:7b',
    'phi3:mini',
    ARES_DEFAULT_MODEL,
]
# preserve order while removing duplicates
DEFAULT_MODEL_CANDIDATES = list(dict.fromkeys(DEFAULT_MODEL_CANDIDATES))
