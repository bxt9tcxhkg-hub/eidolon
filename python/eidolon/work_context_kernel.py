from __future__ import annotations

from typing import Any

from eidolon.work_context_builder import build_unified_work_context
from eidolon.work_context_intent import ACTION_HINTS, OPEN_WORK_PATTERNS, resolve_open_intent
from eidolon.work_context_support import (
    active_workspace,
    candidate_workspace,
    lower_text,
    normalize_text,
    recent_messages,
    topics,
    visible_suggestions,
    workspace_next_actions,
    workspace_summary,
)

__all__ = [
    'ACTION_HINTS',
    'OPEN_WORK_PATTERNS',
    'active_workspace',
    'build_unified_work_context',
    'candidate_workspace',
    'lower_text',
    'normalize_text',
    'recent_messages',
    'resolve_open_intent',
    'topics',
    'visible_suggestions',
    'workspace_next_actions',
    'workspace_summary',
]
