from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterable

from app.core.config import DEFAULT_MODEL_CANDIDATES
from app.core.llm_local import list_local_models
from app.core.private_loader import load_private_module
from app.db.schema import get_conn


@dataclass(slots=True)
class RouteCandidate:
    route_name: str
    model_name: str
    base_score: float
    request_type: str


_PRIVATE_OPTIMIZER = load_private_module('ares_private_optimizer', 'private_optimizer.py')
_HISTORY_CACHE: dict[str, tuple[float, dict[tuple[str, str], float]]] = {}
_HISTORY_TTL_SECONDS = 5.0
_AVAILABLE_MODELS_CACHE: tuple[float, set[str]] | None = None
_MODELS_TTL_SECONDS = 5.0


def extract_features(message: str) -> dict[str, float | str]:
    text = message.strip()
    low = text.lower()
    return {
        'length': float(len(text)),
        'has_question': 1.0 if '?' in text else 0.0,
        'has_code': 1.0 if any(token in low for token in ['code', 'python', 'function', 'bug', 'error']) else 0.0,
        'request_type': 'taskish' if any(token in low for token in ['task', 'remember', 'note']) else 'general',
    }


def _get_available_models() -> set[str]:
    global _AVAILABLE_MODELS_CACHE
    now = time.monotonic()
    if _AVAILABLE_MODELS_CACHE and (now - _AVAILABLE_MODELS_CACHE[0]) < _MODELS_TTL_SECONDS:
        return _AVAILABLE_MODELS_CACHE[1]
    available = set(list_local_models())
    _AVAILABLE_MODELS_CACHE = (now, available)
    return available


def _history_bonus_map(request_type: str) -> dict[tuple[str, str], float]:
    now = time.monotonic()
    cached = _HISTORY_CACHE.get(request_type)
    if cached and (now - cached[0]) < _HISTORY_TTL_SECONDS:
        return cached[1]

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT model_name, request_type, AVG(score) AS avg_score
            FROM optimizer_history
            WHERE request_type=?
            GROUP BY model_name, request_type
            """,
            (request_type,),
        ).fetchall()

    result = {
        (str(row['model_name']), str(row['request_type'])): float(row['avg_score']) * 0.10
        for row in rows
        if row['avg_score'] is not None
    }
    _HISTORY_CACHE[request_type] = (now, result)
    return result


def _invalidate_history_cache(request_type: str | None = None) -> None:
    if request_type is None:
        _HISTORY_CACHE.clear()
        return
    _HISTORY_CACHE.pop(request_type, None)


def build_candidates(features: dict[str, float | str]) -> list[RouteCandidate]:
    available = _get_available_models()
    request_type = str(features['request_type'])
    length = float(features['length'])
    has_code = float(features['has_code'])
    history_bonus = _history_bonus_map(request_type)

    candidates: list[RouteCandidate] = []
    for model in DEFAULT_MODEL_CANDIDATES:
        if model not in available:
            continue
        score = 1.0
        if model.startswith('qwen'):
            score += 0.3 if has_code else 0.0
        if model.startswith('phi3'):
            score += 0.2 if length < 120 else -0.1
        if model.startswith('llama3.1'):
            score += 0.25 if length >= 120 else 0.05
        score += history_bonus.get((model, request_type), 0.0)
        candidates.append(
            RouteCandidate(
                route_name=f'{request_type}:{model}',
                model_name=model,
                base_score=score,
                request_type=request_type,
            )
        )
    return candidates


def pairwise_rank_routes(candidates: Iterable[RouteCandidate]) -> list[RouteCandidate]:
    candidate_list = list(candidates)
    if _PRIVATE_OPTIMIZER and hasattr(_PRIVATE_OPTIMIZER, 'pairwise_rank_routes'):
        return list(_PRIVATE_OPTIMIZER.pairwise_rank_routes(candidate_list))

    wins = [0.0] * len(candidate_list)
    for i in range(len(candidate_list)):
        left = candidate_list[i]
        for j in range(i + 1, len(candidate_list)):
            right = candidate_list[j]
            if left.base_score > right.base_score:
                wins[i] += 1.0
            elif left.base_score < right.base_score:
                wins[j] += 1.0
            else:
                wins[i] += 0.5
                wins[j] += 0.5
    return [
        candidate for _, candidate in sorted(
            ((wins[idx], candidate_list[idx]) for idx in range(len(candidate_list))),
            key=lambda item: (item[0], item[1].base_score),
            reverse=True,
        )
    ]


def select_best_route(message: str) -> RouteCandidate:
    features = extract_features(message)
    candidates = build_candidates(features)
    if not candidates:
        raise RuntimeError(
            'No supported Ollama models are installed. Pull one of: '
            'llama3.1:8b, qwen2.5:7b, phi3:mini'
        )
    ranked = pairwise_rank_routes(candidates)
    return ranked[0]


def record_route_outcome(route: RouteCandidate, score: float, latency_ms: float, success: bool) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO optimizer_history(route_name, model_name, score, latency_ms, success, request_type)
            VALUES(?, ?, ?, ?, ?, ?)
            """,
            (route.route_name, route.model_name, float(score), float(latency_ms), 1 if success else 0, route.request_type),
        )
    _invalidate_history_cache(route.request_type)
