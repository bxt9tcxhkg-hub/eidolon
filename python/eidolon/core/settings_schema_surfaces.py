from __future__ import annotations

from typing import Any


def workspace_defaults() -> dict[str, Any]:
    return {'layout_preference': 'auto', 'seed_topics': [], 'auto_activate': False, 'module_preset': 'generic', 'enabled_modules': ['next_actions', 'status_tracker', 'decision_matrix', 'journal']}


def workspace_enum_rules() -> dict[tuple[str, str], set[str]]:
    return {('workspaces', 'layout_preference'): {'auto', 'hybrid', 'planner', 'tracker', 'decision', 'knowledge', 'review'}, ('workspaces', 'module_preset'): {'generic', 'project', 'knowledge', 'personal'}}


def skills_defaults() -> dict[str, Any]:
    return {'enabled_skills': [], 'disabled_skills': [], 'skill_priorities': {}}


def privacy_defaults() -> dict[str, Any]:
    return {'analytics_enabled': True, 'log_level': 'info', 'retention_days': 365, 'auto_cleanup': True, 'debug_modes': {'network': False, 'llm': False, 'autonomy': False, 'mesh': False, 'proactive': False, 'workspaces': False, 'skills': False, 'healing': False, 'evidence': False, 'code_generation': False}}


def ui_defaults() -> dict[str, Any]:
    return {'language': 'de', 'theme': 'dark', 'density': 'normal', 'animations': True, 'advanced_views': False}


def ui_enum_rules() -> dict[tuple[str, str], set[str]]:
    return {('ui', 'language'): {'de', 'en'}, ('ui', 'theme'): {'dark', 'light', 'system'}, ('ui', 'density'): {'compact', 'normal', 'comfortable'}}
