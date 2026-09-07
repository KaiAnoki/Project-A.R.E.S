from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

from app.core.config import ARES_ENABLE_PRIVATE_OVERRIDES, BASE_DIR


def load_private_module(module_name: str, filename: str) -> ModuleType | None:
    if not ARES_ENABLE_PRIVATE_OVERRIDES:
        return None
    path = BASE_DIR / 'private_overrides' / filename
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
