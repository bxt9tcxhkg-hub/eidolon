from __future__ import annotations

from pathlib import Path

from eidolon.core.config import HTTP_PORT
from eidolon.skills.skill_types import Skill


def builtin_skills() -> dict[str, Skill]:
    return {
        'chat': Skill('chat', 'builtin', ['text'], lambda payload: {'ok': True, 'reply': f"Eidolon: {payload.get('text', '')}"}, description='Allgemeiner Chat-Skill'),
        'runtime_facts': Skill('runtime_facts', 'builtin', ['text'], lambda payload: {'ok': True, 'reply': 'Runtime-Fakten verfügbar'}, description='Liefert Fakten über den LLM-Runtime'),
        'system_info': Skill('system_info', 'builtin', [], lambda payload: {'ok': True, 'reply': f'System-Info: Eidolon 2.0 auf Port {HTTP_PORT}'}, description='System-Informationen'),
        'goal_manager': Skill('goal_manager', 'builtin', ['action', 'goal'], lambda payload: {'ok': True, 'reply': f"Goal: {payload.get('action', 'list')}"}, description='Verwalte autonome Ziele'),
        'device_status': Skill('device_status', 'builtin', [], lambda payload: {'ok': True, 'reply': 'Keine Peers verbunden'}, description='Zeige verbundene Geräte'),
        'mesh_send': Skill('mesh_send', 'builtin', ['peer', 'message'], lambda payload: {'ok': True, 'reply': f"An {payload.get('peer', 'unknown')}: {payload.get('message', '')}"}, description='Nachricht an Peer senden'),
        'note': Skill('note', 'builtin', ['action', 'content'], lambda payload: {'ok': True, 'reply': f"Notiz: {payload.get('action', 'list')}"}, description='Notizen verwalten'),
        'file_organizer': Skill('file_organizer', 'builtin', ['path'], lambda payload: {'ok': True, 'reply': f"Organisiere: {payload.get('path', '.')}"}, description='Dateien organisieren'),
        'calendar': Skill('calendar', 'builtin', ['action'], lambda payload: {'ok': True, 'reply': 'Kalender-Skill'}, description='Kalender-Verwaltung'),
    }


def file_skills(skills_dir: Path, existing: dict[str, Skill]) -> dict[str, Skill]:
    loaded: dict[str, Skill] = {}
    for file in sorted(skills_dir.glob('*.py')):
        if file.name.startswith('_') or file.name.startswith('test_'):
            continue
        name = file.stem
        if name in existing:
            continue
        loaded[name] = Skill(name, 'file', [], lambda payload, _n=name: {'ok': True, 'reply': f"Skill {_n} ausgeführt"}, description=f'Datei-Skill: {file.name}')
    return loaded
