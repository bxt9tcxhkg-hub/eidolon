from __future__ import annotations

from fastapi import FastAPI


def register_code_routes(app: FastAPI, *, apply_llm_code_mutation, code_analyzer, self_reflect_candidates, project_root) -> None:
    @app.post('/code/analyze')
    async def analyze_code(request: dict | None = None):
        file_path = (request or {}).get('file_path', 'python/agent_server.py')
        target = project_root / file_path
        if not target.exists():
            return {'ok': False, 'error': f'Datei nicht gefunden: {file_path}'}
        return {'ok': True, 'analysis': code_analyzer.analyze_file(str(target)), 'file': file_path}

    @app.get('/code/analyze')
    async def analyze_code_get(file_path: str = 'python/agent_server.py'):
        return await analyze_code({'file_path': file_path})

    @app.get('/code/self-reflect')
    async def self_reflect_code(limit: int = 5):
        return {'ok': True, 'supported': True, 'applied': False, 'action': 'self_reflect', 'candidates': self_reflect_candidates(limit=max(1, min(limit, 20)))}

    @app.post('/code/self-reflect')
    async def self_reflect_code_post(request: dict | None = None):
        request = request or {}
        limit = int(request.get('limit') or 5)
        candidates = self_reflect_candidates(limit=max(1, min(limit, 20)))
        if not request.get('apply'):
            return {'ok': True, 'supported': True, 'applied': False, 'action': 'self_reflect', 'candidates': candidates}
        if not candidates:
            return {'ok': False, 'supported': True, 'applied': False, 'action': 'self_reflect', 'error': 'Keine Kandidaten für Self-Reflect gefunden.'}
        target = str(request.get('file_path') or candidates[0]['file'])
        issue = str(request.get('issue') or 'Verbessere Lesbarkeit, Struktur und Wartbarkeit ohne Funktionsänderung.')
        return await apply_llm_code_mutation(action='self_reflect', issue=issue, file_path=target, dry_run=bool(request.get('dry_run', False)))

    @app.post('/code/refactor')
    async def refactor_code(request: dict | None = None):
        request = request or {}
        file_path = request.get('file_path')
        if not file_path:
            return {'ok': False, 'supported': True, 'applied': False, 'action': 'refactor', 'error': 'Kein Dateipfad angegeben'}
        issue = str(request.get('issue') or request.get('goal') or 'Refaktorisiere die Datei für bessere Lesbarkeit und Struktur ohne Verhaltensänderung.')
        return await apply_llm_code_mutation(action='refactor', issue=issue, file_path=str(file_path), dry_run=bool(request.get('dry_run', False)))

    @app.post('/code/fix')
    async def fix_issue(request: dict):
        issue = request.get('issue', '')
        if not issue:
            return {'ok': False, 'error': 'Keine Issue-Beschreibung'}
        target_file = request.get('file_path')
        if target_file:
            target_path = project_root / target_file
            if not target_path.exists() and not str(target_file).startswith('python/'):
                target_path = project_root / 'python' / target_file
            if not target_path.exists():
                return {'ok': False, 'supported': False, 'applied': False, 'file_path': str(target_path.resolve()), 'error': f'Datei nicht gefunden: {target_file}'}
        return await apply_llm_code_mutation(action='fix', issue=issue, file_path=str(target_file), dry_run=bool(request.get('dry_run', False)))
