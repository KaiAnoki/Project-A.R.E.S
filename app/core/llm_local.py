from __future__ import annotations

import requests

from app.core.config import OLLAMA_BASE_URL


class OllamaError(RuntimeError):
    pass


def list_local_models(timeout: float = 5.0) -> list[str]:
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise OllamaError(
            f"Could not reach Ollama at {OLLAMA_BASE_URL}. Make sure Ollama is running."
        ) from exc

    models = payload.get("models", [])
    names: list[str] = []
    for item in models:
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return names


def generate(model: str, prompt: str, timeout: float = 120.0) -> tuple[str, float]:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise OllamaError(
            f"Local generation failed for model '{model}'. Verify the model is installed in Ollama and Ollama is running."
        ) from exc

    text = payload.get("response", "")
    if not isinstance(text, str):
        text = str(text)

    total_duration = payload.get("total_duration", 0)
    try:
        latency_ms = float(total_duration) / 1_000_000
    except Exception:
        latency_ms = 0.0
    return text.strip(), latency_ms
