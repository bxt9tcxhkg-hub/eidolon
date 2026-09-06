from __future__ import annotations

from threading import Lock
from typing import Any

PHASE_IDLE = 'idle'
PHASE_DENKT = 'denkt'
PHASE_ARBEITET = 'arbeitet'
PHASE_ANTWORTET = 'antwortet'

PHASE_LABELS = {
    PHASE_IDLE: '',
    PHASE_DENKT: 'denkt…',
    PHASE_ARBEITET: 'arbeitet…',
    PHASE_ANTWORTET: 'antwortet',
}

INSTRUMENTED_PHASES = (PHASE_DENKT, PHASE_ARBEITET, PHASE_ANTWORTET)

_lock = Lock()
_turns: dict[str, dict[str, Any]] = {}


def reset_chat_turn_status() -> None:
    with _lock:
        _turns.clear()


def set_chat_turn_phase(session_id: str | None, phase: str, reason: str) -> dict[str, Any]:
    sid = str(session_id or '').strip()
    if not sid:
        return snapshot_chat_turn(None)
    if phase not in PHASE_LABELS:
        raise ValueError(f'Unbekannte Chat-Phase: {phase}')
    snapshot = {
        'session_id': sid,
        'phase': phase,
        'label': PHASE_LABELS[phase],
        'reason': str(reason or ''),
        'instrumented': list(INSTRUMENTED_PHASES),
    }
    with _lock:
        if phase == PHASE_IDLE:
            _turns.pop(sid, None)
        else:
            _turns[sid] = snapshot
    return snapshot


def clear_chat_turn_phase(session_id: str | None) -> dict[str, Any]:
    return set_chat_turn_phase(session_id, PHASE_IDLE, 'cleared')


def snapshot_chat_turn(session_id: str | None) -> dict[str, Any]:
    sid = str(session_id or '').strip()
    with _lock:
        if sid and sid in _turns:
            return dict(_turns[sid])
    return {
        'session_id': sid or None,
        'phase': PHASE_IDLE,
        'label': PHASE_LABELS[PHASE_IDLE],
        'reason': 'idle',
        'instrumented': list(INSTRUMENTED_PHASES),
    }
