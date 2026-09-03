from __future__ import annotations

LIVE_CONTEXT_SOURCES = {'chat', 'workspace_input', 'project', 'project_inbox', 'user'}
IGNORED_SOURCE_PREFIXES = ('verification', 'block-', 'block_', 'seed', 'test')
IGNORED_SOURCES = {'eidolon-cli', 'system', 'migration'}


def is_live_context_source(source: str | None) -> bool:
    normalized = str(source or '').strip().lower()
    if not normalized:
        return False
    if normalized in LIVE_CONTEXT_SOURCES:
        return True
    if normalized in IGNORED_SOURCES:
        return False
    return not any(normalized.startswith(prefix) for prefix in IGNORED_SOURCE_PREFIXES)
