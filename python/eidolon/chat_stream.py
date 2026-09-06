"""Honest SSE encoding for chat turns.

Deltas are only emitted when an LLM provider actually streamed tokens.
Immediate paths (truth, settings, skills) and non-streamable providers
finish as a single `done` event — no typewriter of a finished string.
"""
from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from typing import Any

from fastapi.responses import StreamingResponse

from eidolon.chat_error_support import sanitize_chat_error
from eidolon.chat_turn_status import PHASE_ANTWORTET, PHASE_DENKT

SSE_MEDIA_TYPE = 'text/event-stream'
SSE_HEADERS = {
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',
}


def format_sse(payload: dict[str, Any]) -> str:
    return f'data: {json.dumps(payload, ensure_ascii=False)}\n\n'


def parse_sse_events(body: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for block in body.split('\n\n'):
        lines = [line[5:].strip() for line in block.splitlines() if line.startswith('data:')]
        if not lines:
            continue
        raw = '\n'.join(lines)
        if raw == '[DONE]':
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
    return events


def sse_response(events: Iterator[str]) -> StreamingResponse:
    return StreamingResponse(events, media_type=SSE_MEDIA_TYPE, headers=SSE_HEADERS)


def immediate_sse(payload: dict[str, Any], *, phase: str | None = None) -> StreamingResponse:
    def events() -> Iterator[str]:
        yield format_sse({'type': 'start', 'session_id': payload.get('session_id'), 'phase': 'denkt'})
        if phase and phase != 'denkt':
            yield format_sse({'type': 'phase', 'phase': phase})
        yield format_sse({'type': 'done', 'streamed': False, **payload})

    return sse_response(events())


def llm_sse_response(
    *,
    session_id: str,
    runtime_context: dict[str, Any],
    compiled_system_prompt: str,
    user_prompt: str,
    llm_backend,
    finalize_chat_reply: Callable[[str, dict[str, Any]], tuple[str, dict[str, Any]]],
    build_grounded_fallback_reply: Callable[[dict[str, Any]], str],
    chat_session_store,
    mark_phase: Callable[[str | None, str, str], None],
) -> StreamingResponse:
    def events() -> Iterator[str]:
        yield format_sse({'type': 'start', 'session_id': session_id, 'phase': PHASE_DENKT})
        acc: list[str] = []
        streamed = False
        try:
            mark_phase(session_id, PHASE_DENKT, 'llm_stream')
            for item in llm_backend.iter_reply(compiled_system_prompt, user_prompt, prefer_stream=True):
                kind = item.get('kind')
                if kind == 'delta':
                    text = str(item.get('text') or '')
                    if not text:
                        continue
                    if not streamed:
                        mark_phase(session_id, PHASE_ANTWORTET, 'llm_stream')
                        yield format_sse({'type': 'phase', 'phase': PHASE_ANTWORTET})
                    streamed = True
                    acc.append(text)
                    yield format_sse({'type': 'delta', 'text': text})
                elif kind == 'complete':
                    acc = [str(item.get('text') or '')]
                    streamed = False
            reply = ''.join(acc)
            mark_phase(session_id, PHASE_ANTWORTET, 'finalize_reply')
            raw = reply
            reply, quality = finalize_chat_reply(reply, runtime_context)
            if not str(reply).strip():
                reply = build_grounded_fallback_reply(runtime_context)
                quality['used_fallback'] = True
                quality['contract_satisfied'] = True
            if reply != raw:
                yield format_sse({'type': 'replace', 'text': reply})
            chat_session_store.append_message(session_id, 'assistant', reply)
            yield format_sse({
                'type': 'done',
                'ok': True,
                'response': reply,
                'streamed': streamed,
                'provider': llm_backend.status(),
                'session_id': session_id,
                'runtime_context': runtime_context,
                'response_quality': quality,
            })
        except Exception as exc:
            assistant_message, public_error, error_code = sanitize_chat_error(exc)
            mark_phase(session_id, PHASE_ANTWORTET, 'chat_error')
            chat_session_store.append_message(session_id, 'assistant', f'Fehler: {assistant_message}')
            yield format_sse({
                'type': 'error',
                'ok': False,
                'error': public_error,
                'error_code': error_code,
                'session_id': session_id,
                'runtime_context': runtime_context,
                'streamed': streamed,
            })

    return sse_response(events())
