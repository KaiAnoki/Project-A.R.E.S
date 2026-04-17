from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, List

from app.db.schema import get_conn

TOKEN_RE = re.compile(r"[a-zA-Z0-9_']+")
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'how', 'i', 'in', 'is',
    'it', 'me', 'my', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 'when',
    'where', 'who', 'why', 'with', 'you', 'your'
}


@dataclass(slots=True)
class _CorpusDoc:
    item: dict
    tokens: list[str]
    token_set: set[str]
    vector: dict[str, float]


@dataclass(slots=True)
class _CorpusCache:
    signature: tuple[int, int]
    idf: dict[str, float]
    docs: list[_CorpusDoc]


_CORPUS_CACHE: _CorpusCache | None = None


def _invalidate_corpus_cache() -> None:
    global _CORPUS_CACHE
    _CORPUS_CACHE = None


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(text.lower()) if token.lower() not in STOPWORDS]


def _term_frequency(tokens: Iterable[str]) -> Counter[str]:
    return Counter(tokens)


def _inverse_document_frequency(documents: list[list[str]]) -> dict[str, float]:
    total_docs = max(1, len(documents))
    doc_freq: Counter[str] = Counter()
    for doc in documents:
        for token in set(doc):
            doc_freq[token] += 1
    return {token: math.log((1 + total_docs) / (1 + freq)) + 1.0 for token, freq in doc_freq.items()}


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    shared_terms = left.keys() & right.keys()
    if not shared_terms:
        return 0.0
    dot = sum(left[term] * right[term] for term in shared_terms)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


def _tfidf_vector(tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
    tf = _term_frequency(tokens)
    if not tf:
        return {}
    max_tf = max(tf.values())
    return {term: (count / max_tf) * idf.get(term, 1.0) for term, count in tf.items()}


def _load_corpus() -> _CorpusCache:
    global _CORPUS_CACHE

    with get_conn() as conn:
        row = conn.execute(
            'SELECT COUNT(*) AS count_rows, COALESCE(MAX(id), 0) AS max_id FROM memories'
        ).fetchone()
        signature = (int(row['count_rows']), int(row['max_id']))
        if _CORPUS_CACHE is not None and _CORPUS_CACHE.signature == signature:
            return _CORPUS_CACHE

        rows = conn.execute(
            'SELECT id, content, source, created_at FROM memories ORDER BY id DESC'
        ).fetchall()

    documents = [dict(row) for row in rows]
    doc_tokens = [_tokenize(item['content']) for item in documents]
    idf = _inverse_document_frequency(doc_tokens)
    docs = [
        _CorpusDoc(
            item=item,
            tokens=tokens,
            token_set=set(tokens),
            vector=_tfidf_vector(tokens, idf),
        )
        for item, tokens in zip(documents, doc_tokens)
    ]
    _CORPUS_CACHE = _CorpusCache(signature=signature, idf=idf, docs=docs)
    return _CORPUS_CACHE


def save_chat(role: str, message: str) -> None:
    clean_role = role.strip()
    clean_message = message.strip()
    if not clean_role or not clean_message:
        return
    with get_conn() as conn:
        conn.execute(
            'INSERT INTO chats(role, message) VALUES(?, ?)',
            (clean_role, clean_message),
        )


def get_recent_chat(limit: int = 8) -> List[dict]:
    safe_limit = max(1, int(limit))
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT role, message FROM chats ORDER BY id DESC LIMIT ?',
            (safe_limit,),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def remember(content: str, source: str = 'manual') -> int:
    clean = content.strip()
    clean_source = source.strip() or 'manual'
    if not clean:
        raise ValueError('Memory content was empty.')
    with get_conn() as conn:
        cur = conn.execute(
            'INSERT INTO memories(content, source) VALUES(?, ?)',
            (clean, clean_source),
        )
        memory_id = int(cur.lastrowid)
    _invalidate_corpus_cache()
    return memory_id


def recall(query: str, limit: int = 5) -> list[dict]:
    clean_query = query.strip()
    if not clean_query:
        return []
    safe_limit = max(1, int(limit))
    corpus = _load_corpus()
    if not corpus.docs:
        return []

    query_tokens = _tokenize(clean_query)
    if not query_tokens:
        return []

    query_idf = dict(corpus.idf)
    unseen_weight = math.log((1 + len(corpus.docs) + 1) / 1) + 1.0
    for token in query_tokens:
        query_idf.setdefault(token, unseen_weight)
    query_vector = _tfidf_vector(query_tokens, query_idf)
    query_token_set = set(query_tokens)

    scored: list[dict] = []
    for doc in corpus.docs:
        lexical_overlap = len(doc.token_set & query_token_set)
        score = _cosine_similarity(query_vector, doc.vector) + (0.05 * lexical_overlap)
        if score <= 0.0:
            continue
        enriched = dict(doc.item)
        enriched['score'] = round(score, 4)
        scored.append(enriched)

    scored.sort(key=lambda entry: (entry['score'], entry['id']), reverse=True)
    return scored[:safe_limit]


def build_rag_context(query: str, limit: int = 5) -> str:
    matches = recall(query, limit=limit)
    if not matches:
        return 'No relevant memory retrieved.'

    blocks = []
    for index, item in enumerate(matches, start=1):
        blocks.append(
            f"[{index}] source={item['source']} score={item['score']} memory={item['content']}"
        )
    return '\n'.join(blocks)
