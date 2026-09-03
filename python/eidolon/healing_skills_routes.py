from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI

from eidolon.core.config import state_path


def register_healing_skills_routes(
    app: FastAPI,
    *,
    project_root: Path,
    get_healing_service: Callable[[], Any],
    get_builtin_skills: Callable[[], list[dict[str, Any]]],
) -> None:
    def healing_service():
        return get_healing_service()

    def builtin_skills():
        return get_builtin_skills()

    def _find_builtin_skill(name: str) -> dict | None:
        for skill in builtin_skills():
            if skill.get('name') == name:
                return skill
        return None

    @app.get('/healing/status')
    async def healing_status():
        state = healing_service().get_state()
        last_event = None
        events = []
        log_path = state_path('healing', 'events.json', project_root=project_root)
        if log_path.exists():
            try:
                events = json.loads(log_path.read_text(encoding='utf-8'))[-10:]
                last_event = events[-1] if events else None
            except Exception:
                events = []
        return {
            'status': 'running' if state.get('running') else 'stopped',
            'available': bool(state.get('running')),
            'checks_registered': state.get('checks_registered', []),
            'total_checks': state.get('total_checks', 0),
            'total_recoveries': state.get('total_recoveries', 0),
            'error_counts': state.get('error_counts', {}),
            'events': events,
            'last_event': last_event,
            'detail': 'SelfHealingService ist verdrahtet und führt reale registrierte Checks aus.' if state.get('running') else 'SelfHealingService ist verdrahtet, aber aktuell gestoppt.',
        }

    @app.post('/healing/check')
    async def healing_check():
        result = await healing_service().run_check_cycle()
        return {'ok': True, 'cycle': result, 'state': healing_service().get_state()}

    @app.get('/skills')
    async def list_skills():
        return {'ok': True, 'skills': builtin_skills()}

    @app.get('/skills/enabled')
    async def list_enabled_skills():
        return {'ok': True, 'skills': [skill for skill in builtin_skills() if skill.get('enabled')]}

    @app.post('/skills/{name}/enable')
    async def enable_skill(name: str):
        skill = _find_builtin_skill(name)
        if not skill:
            return {'ok': False, 'error': 'Skill nicht gefunden'}
        skill['enabled'] = True
        return {'ok': True, 'skill': skill, 'enabled': True}

    @app.post('/skills/{name}/disable')
    async def disable_skill(name: str):
        skill = _find_builtin_skill(name)
        if not skill:
            return {'ok': False, 'error': 'Skill nicht gefunden'}
        skill['enabled'] = False
        return {'ok': True, 'skill': skill, 'enabled': False}

    @app.post('/skills/{name}/toggle')
    async def toggle_skill(name: str):
        skill = _find_builtin_skill(name)
        if not skill:
            return {'ok': False, 'error': 'Skill nicht gefunden'}
        skill['enabled'] = not bool(skill.get('enabled'))
        return {'ok': True, 'skill': skill, 'enabled': skill['enabled']}

    @app.put('/skills/{name}/priority')
    async def set_skill_priority(name: str, request: dict):
        skill = _find_builtin_skill(name)
        if not skill:
            return {'ok': False, 'error': 'Skill nicht gefunden'}
        priority = int(request.get('priority', 0))
        skill['priority'] = priority
        return {'ok': True, 'skill': skill, 'priority': priority}
