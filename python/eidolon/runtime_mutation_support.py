from __future__ import annotations

import ast
from pathlib import Path
from typing import Any


def extract_python_candidate(raw: str) -> str:
    text = str(raw or '').strip()
    if '```' in text:
        for chunk in text.split('```'):
            chunk = chunk.strip()
            if not chunk:
                continue
            if chunk.startswith('python'):
                return chunk[len('python'):].lstrip(chr(13) + chr(10))
            if 'def ' in chunk or 'class ' in chunk or '=' in chunk:
                return chunk
    return text


async def apply_llm_code_mutation(
    *,
    action: str,
    issue: str,
    file_path: str,
    project_root: Path,
    llm_backend: Any,
    system_prompt: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    target = project_root / str(file_path)
    if not target.exists():
        return {'ok': False, 'supported': False, 'applied': False, 'action': action, 'file_path': str(target), 'error': f'Datei nicht gefunden: {file_path}'}
    before = target.read_text(encoding='utf-8')
    prompt = 'Aktion: ' + action + chr(10) + 'Datei: ' + file_path + chr(10) + 'Ziel: ' + issue + chr(10) + 'Liefere den vollständigen neuen Python-Dateiinhalt ohne Erklärtext.'
    candidate_raw = await llm_backend.complete(system_prompt, prompt)
    candidate = extract_python_candidate(candidate_raw)
    if not candidate.strip() or candidate.strip() == before.strip():
        return {'ok': True, 'supported': True, 'applied': False, 'action': action, 'file_path': file_path, 'change_type': 'proposal_only', 'validation': 'no_change'}
    try:
        ast.parse(candidate)
    except SyntaxError as exc:
        return {'ok': False, 'supported': True, 'applied': False, 'action': action, 'file_path': file_path, 'change_type': 'proposal_only', 'error': f'Syntax-Fehler im Vorschlag: {exc}'}
    if dry_run:
        return {'ok': True, 'supported': True, 'applied': False, 'action': action, 'file_path': file_path, 'change_type': 'proposal_only', 'validation': 'dry_run_validated', 'proposal': candidate}
    target.write_text(candidate, encoding='utf-8')
    try:
        ast.parse(target.read_text(encoding='utf-8'))
    except SyntaxError as exc:
        target.write_text(before, encoding='utf-8')
        return {'ok': False, 'supported': True, 'applied': False, 'action': action, 'file_path': file_path, 'error': f'Rollback nach Syntax-Fehler: {exc}'}
    return {'ok': True, 'supported': True, 'applied': True, 'action': action, 'file_path': file_path, 'validation': 'py_compile_ok'}
