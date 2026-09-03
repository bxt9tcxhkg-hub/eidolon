from __future__ import annotations

VALID_TRANSITIONS: dict[str, dict[str, list[str]]] = {
    'project': {
        'backlog': ['ready', 'cancelled'],
        'ready': ['in_progress', 'blocked', 'cancelled'],
        'in_progress': ['review', 'blocked', 'ready'],
        'review': ['done', 'in_progress', 'blocked'],
        'blocked': ['ready', 'cancelled'],
        'done': ['in_progress'],
        'cancelled': ['backlog'],
    },
    'knowledge': {
        'draft': ['review', 'archived'],
        'review': ['published', 'draft'],
        'published': ['archived', 'draft'],
        'archived': ['draft'],
    },
    'personal': {
        'todo': ['doing', 'delegated', 'cancelled'],
        'doing': ['done', 'blocked', 'todo'],
        'blocked': ['doing', 'cancelled'],
        'delegated': ['done', 'doing'],
        'done': ['doing'],
        'cancelled': ['todo'],
    },
}

DOMAIN_MODULES: dict[str, list[str]] = {
    'project': ['board', 'graph', 'dependencies', 'next_actions', 'details', 'timeline'],
    'knowledge': ['map', 'notes', 'sources', 'review', 'tags'],
    'personal': ['tasks', 'habits', 'journal', 'goals', 'tracking'],
}
