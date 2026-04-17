from __future__ import annotations

from app.core import memory, tools
from app.core.llm_local import OllamaError, generate
from app.core.optimizer import record_route_outcome, select_best_route
from app.core.private_loader import load_private_module
from app.core.router import classify_intent


_PRIVATE_PROMPTS = load_private_module('ares_private_prompts', 'private_prompts.py')
SYSTEM_PROMPT = (
    getattr(_PRIVATE_PROMPTS, 'SYSTEM_PROMPT', None)
    or 'You are ARES, a serious local personal AI assistant built for one user. '
       'Be clear, direct, and useful. Do not claim to have completed actions you did not complete.'
)


def _handle_tool_intent(message: str):
    intent = classify_intent(message)
    if intent.intent == 'add_task':
        return tools.add_task(intent.argument or '')
    if intent.intent == 'list_tasks':
        return tools.list_tasks()
    if intent.intent == 'complete_task':
        if intent.task_id is None:
            return 'Please provide a valid task id.'
        return tools.complete_task(intent.task_id)
    if intent.intent == 'remember':
        return tools.remember_note(intent.argument or '')
    if intent.intent == 'recall':
        return tools.recall_memory(intent.argument or '')
    if intent.intent == 'create_note':
        return tools.create_note(intent.argument or '')
    if intent.intent == 'list_notes':
        return tools.list_notes()
    return None


def _build_prompt(message: str) -> str:
    recent = memory.get_recent_chat(limit=8)
    rag_context = memory.build_rag_context(message, limit=5)
    lines = [
        SYSTEM_PROMPT,
        '',
        'Retrieved memory context:',
        rag_context,
        '',
        'Recent conversation:',
    ]
    for item in recent:
        lines.append(f"{item['role']}: {item['message']}")
    lines.extend([
        '',
        'Instructions:',
        '- Use the retrieved memory context when it is relevant to the user request.',
        '- If the retrieved memory context is not relevant, ignore it.',
        '- Do not invent tool actions or claimed side effects.',
        '',
        f'user: {message}',
        'assistant:',
    ])
    return '\n'.join(lines)


def process_message(message: str) -> dict:
    clean = message.strip()
    if not clean:
        return {'reply': 'Please enter a message.'}

    memory.save_chat('user', clean)
    tool_reply = _handle_tool_intent(clean)
    if tool_reply is not None:
        memory.save_chat('assistant', tool_reply)
        return {'reply': tool_reply, 'mode': 'tool'}

    try:
        route = select_best_route(clean)
        prompt = _build_prompt(clean)
        reply, latency_ms = generate(route.model_name, prompt)
        if not reply:
            reply = 'ARES generated an empty response.'
        score = max(0.1, min(1.0, 1.0 - (latency_ms / 20000.0)))
        record_route_outcome(route, score=score, latency_ms=latency_ms, success=True)
        memory.save_chat('assistant', reply)
        return {
            'reply': reply,
            'mode': 'local_llm',
            'model': route.model_name,
            'route': route.route_name,
            'latency_ms': latency_ms,
            'rag_context': memory.build_rag_context(clean, limit=3),
        }
    except (RuntimeError, OllamaError) as exc:
        error_reply = str(exc)
        memory.save_chat('assistant', error_reply)
        return {'reply': error_reply, 'mode': 'error'}
