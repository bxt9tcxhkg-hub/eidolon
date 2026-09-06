from __future__ import annotations

from pathlib import Path

from eidolon.skills.live_skills import LIVE_SKILL_IDS, execute_live_skill, unwired_skill_reply
from eidolon.skills.skill_types import Skill

_SKIP_FILE_STEMS = frozenset({
    'builtin',
    'builtin_handlers',
    'chat_skill_turn',
    'live_skills',
    'plugin',
    'registry',
    'runtime',
    'skill_catalog',
    'skill_routing',
    'skill_state',
    'skill_types',
})

_FILE_NAME_ALIASES = {
    'system-info': 'system_info',
    'device-status': 'device_status',
    'file-organizer': 'file_organizer',
    'mesh-send': 'mesh_send',
    'goal-manager': 'goal_manager',
    'calendar-summarize': 'calendar',
    'skill-generator': 'skill-generator',
}


def _live_fn(name: str):
    def fn(payload: dict) -> dict:
        return execute_live_skill(name, payload or {})
    return fn


def _unwired_fn(name: str):
    def fn(payload: dict) -> dict:
        return {
            'ok': False,
            'wired': False,
            'executed': False,
            'skill': name,
            'reply': unwired_skill_reply(name),
        }
    return fn


def _skill(name: str, params: list[str], description: str) -> Skill:
    live = name in LIVE_SKILL_IDS
    return Skill(
        name,
        'file' if live else 'catalog',
        params,
        _live_fn(name) if live else _unwired_fn(name),
        description=description,
        executable=live,
        runtime_wired=live,
    )


def builtin_skills() -> dict[str, Skill]:
    return {
        'chat': _skill('chat', ['text'], 'Allgemeiner Chat-Skill'),
        'runtime_facts': _skill('runtime_facts', ['text'], 'Liefert Fakten über den LLM-Runtime'),
        'system_info': _skill('system_info', [], 'System-Informationen vom Host'),
        'goal_manager': _skill('goal_manager', ['action', 'goal'], 'Verwalte autonome Ziele'),
        'device_status': _skill('device_status', [], 'Geräte und Mesh-Inbox'),
        'mesh_send': _skill('mesh_send', ['peer', 'message'], 'Nachricht an Peer senden'),
        'note': _skill('note', ['action', 'content'], 'Notizen in notes.json'),
        'file_organizer': _skill('file_organizer', ['path'], 'Dateien organisieren'),
        'calendar': _skill('calendar', ['action'], 'Kalender-Verwaltung'),
    }


def file_skills(skills_dir: Path, existing: dict[str, Skill]) -> dict[str, Skill]:
    loaded: dict[str, Skill] = {}
    for file in sorted(Path(skills_dir).glob('*.py')):
        if file.name.startswith('_') or file.name.startswith('test_'):
            continue
        stem = file.stem
        if stem in _SKIP_FILE_STEMS:
            continue
        name = _FILE_NAME_ALIASES.get(stem, stem)
        if name in existing or name in loaded:
            continue
        live = name in LIVE_SKILL_IDS
        loaded[name] = Skill(
            name,
            'file',
            [],
            _live_fn(name) if live else _unwired_fn(name),
            description=f'Datei-Skill: {file.name}',
            executable=live,
            runtime_wired=live,
        )
    return loaded
