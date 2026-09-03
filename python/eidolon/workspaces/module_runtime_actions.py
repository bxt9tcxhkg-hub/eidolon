from __future__ import annotations

from typing import Any, Callable

from eidolon.workspaces.module_runtime_actions_board import apply_board_action
from eidolon.workspaces.module_runtime_actions_graph import apply_graph_action
from eidolon.workspaces.module_runtime_actions_misc import (
    apply_decision_matrix_action,
    apply_dependencies_action,
    apply_details_action,
    apply_fallback_action,
    apply_journal_action,
    apply_next_actions_action,
    apply_status_tracker_action,
)


ModuleHandler = Callable[[dict[str, Any], dict[str, Any], str, dict[str, Any]], tuple[dict[str, Any], str | None]]


def _status_tracker_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_status_tracker_action(current, action, payload), None


def _decision_matrix_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_decision_matrix_action(current, action, payload), None


def _next_actions_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_next_actions_action(current, state, action, payload), None


def _board_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_board_action(current, {**payload, '_action': action})


def _graph_handler(module_data: dict[str, Any], current: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_graph_action(module_data, current, {**payload, '_action': action}), None


def _details_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_details_action(current, action, payload), None


def _dependencies_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_dependencies_action(current, action, payload), None


def _journal_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_journal_action(current, {**payload, '_action': action}), None


def _fallback_handler(current: dict[str, Any], state: dict[str, Any], action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    return apply_fallback_action(current, action, payload), None


def apply_module_action(module_data: dict[str, Any], state: dict[str, Any], module_id: str, action: str, payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    current = dict(module_data.get(module_id) or {})
    handlers: dict[str, ModuleHandler] = {
        'status_tracker': lambda current, state, action, payload: _status_tracker_handler(current, state, action, payload),
        'decision_matrix': lambda current, state, action, payload: _decision_matrix_handler(current, state, action, payload),
        'next_actions': lambda current, state, action, payload: _next_actions_handler(current, state, action, payload),
        'board': lambda current, state, action, payload: _board_handler(current, state, action, payload),
        'details': lambda current, state, action, payload: _details_handler(current, state, action, payload),
        'dependencies': lambda current, state, action, payload: _dependencies_handler(current, state, action, payload),
        'journal': lambda current, state, action, payload: _journal_handler(current, state, action, payload),
        'reflection': lambda current, state, action, payload: _journal_handler(current, state, action, payload),
    }
    if module_id == 'graph':
        current, focus_card_id = _graph_handler(module_data, current, action, payload)
    else:
        handler = handlers.get(module_id, lambda current, state, action, payload: _fallback_handler(current, state, action, payload))
        current, focus_card_id = handler(current, state, action, payload)
    module_data[module_id] = current
    return module_data, current, focus_card_id
