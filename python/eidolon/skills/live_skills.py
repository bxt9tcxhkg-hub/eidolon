"""Small honest set of chat-executable skills.

Only handlers that really read or write state belong here.
Catalog names without a live handler stay unwired — no echo success.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

SKILLS_DIR = Path(__file__).resolve().parent

# Canonical chat names → file stem (hyphenated modules).
LIVE_SKILL_MODULES = {
    'note': 'note',
    'system_info': 'system-info',
    'device_status': 'device-status',
}

LIVE_SKILL_IDS = frozenset(LIVE_SKILL_MODULES)

# Catalog names that exist as list entries or file skills but are not chat-wired.
CATALOG_SKILL_IDS = frozenset({
    'chat',
    'runtime_facts',
    'goal_manager',
    'mesh_send',
    'file_organizer',
    'calendar',
    'calendar-summarize',
    'skill-generator',
    'skill_generator',
})

_MODULE_CACHE: dict[str, Any] = {}


def is_live_skill(name: str) -> bool:
    return str(name or '') in LIVE_SKILL_IDS


def _load_skill_module(stem: str):
    if stem in _MODULE_CACHE:
        return _MODULE_CACHE[stem]
    path = SKILLS_DIR / f'{stem}.py'
    if not path.exists():
        raise FileNotFoundError(f'Skill-Modul fehlt: {stem}')
    spec = importlib.util.spec_from_file_location(f'eidolon_live_skill_{stem.replace("-", "_")}', path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Skill-Modul nicht ladbar: {stem}')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _MODULE_CACHE[stem] = mod
    return mod


def execute_live_skill(name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Call the real file handler. Never invents a success."""
    canonical = str(name or '')
    stem = LIVE_SKILL_MODULES.get(canonical)
    if not stem:
        return {
            'ok': False,
            'wired': False,
            'executed': False,
            'skill': canonical,
            'error': f'Skill ist nicht als Runtime verdrahtet: {canonical}',
        }
    params = dict(payload or {})
    try:
        mod = _load_skill_module(stem)
        handler = getattr(mod, 'run', None)
        if not callable(handler):
            return {
                'ok': False,
                'wired': True,
                'executed': False,
                'skill': canonical,
                'error': f'Skill {canonical} hat keinen run()-Handler',
            }
        result = handler(params)
        if not isinstance(result, dict):
            result = {'value': result}
        if result.get('error') and not result.get('status') and 'total_notes' not in result:
            return {
                'ok': False,
                'wired': True,
                'executed': True,
                'skill': canonical,
                'result': result,
                'error': str(result.get('error')),
            }
        return {
            'ok': True,
            'wired': True,
            'executed': True,
            'skill': canonical,
            'result': result,
        }
    except Exception as exc:
        return {
            'ok': False,
            'wired': True,
            'executed': True,
            'skill': canonical,
            'error': f'{type(exc).__name__}: {exc}',
        }


def unwired_skill_reply(name: str) -> str:
    labels = {
        'calendar': 'Kalender',
        'calendar-summarize': 'Kalender',
        'file_organizer': 'Dateien organisieren',
        'mesh_send': 'Mesh-Send',
        'goal_manager': 'Goal-Manager',
        'runtime_facts': 'Runtime-Fakten',
        'chat': 'Chat',
        'skill-generator': 'Skill-Generator',
        'skill_generator': 'Skill-Generator',
    }
    label = labels.get(name, name or 'diese Fähigkeit')
    extras = {
        'calendar': ' Es gibt keinen Kalender-Anschluss — ich erfinde keine Termine.',
        'calendar-summarize': ' Es gibt keinen Kalender-Anschluss — ich erfinde keine Termine.',
        'file_organizer': ' Dateien werden nicht still verschoben.',
        'mesh_send': ' Es gibt keinen Peer-Versand aus diesem Gespräch.',
        'goal_manager': ' Autonomie-Ziele liegen unter Mehr, nicht als Chat-Skill.',
        'runtime_facts': ' Modell und Provider beantworte ich direkt, wenn du danach fragst.',
        'chat': ' Chat ist das Gespräch, kein ausführbarer Skill.',
        'skill-generator': ' Es werden keine neuen Fähigkeiten geschrieben.',
        'skill_generator': ' Es werden keine neuen Fähigkeiten geschrieben.',
    }
    extra = extras.get(name, ' Ich erfinde keine Ausführung.')
    return f'Die Fähigkeit „{label}“ ist im Katalog, aber nicht als Runtime verdrahtet.{extra}'


def format_live_skill_reply(name: str, outcome: dict[str, Any]) -> str:
    if not outcome.get('ok'):
        error = str(outcome.get('error') or 'Ausführung fehlgeschlagen')
        return f'Skill „{name}“ ist verdrahtet, ist aber fehlgeschlagen: {error}'
    result = outcome.get('result') or {}
    if name == 'system_info':
        return _format_system_info(result)
    if name == 'note':
        return _format_note(result)
    if name == 'device_status':
        return _format_device_status(result)
    return f'Skill „{name}“ hat echte Daten geliefert.'


def _format_bytes_gb(value: Any) -> str:
    try:
        return f'{float(value) / 1024 ** 3:.1f} GB'
    except (TypeError, ValueError):
        return '—'


def _format_system_info(result: dict[str, Any]) -> str:
    memory = result.get('memory') if isinstance(result.get('memory'), dict) else {}
    disk = result.get('disk') if isinstance(result.get('disk'), dict) else {}
    lines = [
        'System-Info (echt vom Host):',
        f"- System: {result.get('system') or 'unbekannt'} {result.get('release') or ''}".rstrip(),
        f"- Rechner: {result.get('node') or 'unbekannt'}",
        f"- Maschine: {result.get('machine') or 'unbekannt'}",
    ]
    if 'cpu_percent' in result:
        lines.append(f"- CPU: {result.get('cpu_percent')} %")
    if memory:
        lines.append(
            f"- Speicher: {_format_bytes_gb(memory.get('used'))} / {_format_bytes_gb(memory.get('total'))}"
            f" ({memory.get('percent', '—')} %)"
        )
    if disk:
        free = disk.get('free')
        lines.append(f"- Platte frei: {_format_bytes_gb(free)}")
    return '\n'.join(lines)


def _format_note(result: dict[str, Any]) -> str:
    status = str(result.get('status') or '')
    notes = result.get('notes') if isinstance(result.get('notes'), list) else None
    total = result.get('total_notes')
    if status == 'liste' or notes is not None:
        if not notes:
            return 'Keine Notizen gespeichert.'
        lines = [f'{len(notes)} Notizen:']
        for item in notes[-8:]:
            if not isinstance(item, dict):
                lines.append(f'- {item}')
                continue
            stamp = str(item.get('timestamp') or '')[:19]
            text = str(item.get('note') or '')
            lines.append(f'- {stamp}: {text}' if stamp else f'- {text}')
        if total and int(total) > len(notes[-8:]):
            lines.append(f'… {int(total) - 8} weitere in notes.json')
        return '\n'.join(lines)
    note = str(result.get('note') or '')
    count = total if total is not None else 1
    if note:
        return f'Notiz gespeichert: {note}. Du hast jetzt {count} Notizen.'
    return f'Notiz gespeichert. Du hast jetzt {count} Notizen.'


def _format_device_status(result: dict[str, Any]) -> str:
    devices = result.get('devices') if isinstance(result.get('devices'), list) else []
    connected = result.get('connected_devices')
    if connected is None:
        connected = len(devices)
    pending = result.get('pending_messages')
    inbox_total = result.get('inbox_total')
    lines = [
        'Geräte-Status (Mesh-Store):',
        f'- {connected} Geräte in devices.json',
    ]
    if inbox_total is not None:
        open_bit = f', {pending} offen' if pending is not None else ''
        lines.append(f'- Inbox: {inbox_total} Nachrichten{open_bit}')
    if devices:
        for item in devices[:5]:
            if isinstance(item, dict):
                label = item.get('name') or item.get('peer_id') or item.get('id') or 'Gerät'
                lines.append(f'- {label}')
            else:
                lines.append(f'- {item}')
    return '\n'.join(lines)
