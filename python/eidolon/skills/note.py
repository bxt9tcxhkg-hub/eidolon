"""Notiz-Skill: Merkt Informationen und speichert sie persistent."""
import json
from datetime import datetime

from eidolon.core.config import state_path


def run(params: dict) -> dict:
    data_dir = state_path('persistence', 'notes.json')
    data_dir.parent.mkdir(parents=True, exist_ok=True)

    notes = []
    if data_dir.exists():
        try:
            loaded = json.loads(data_dir.read_text(encoding='utf-8'))
            notes = loaded if isinstance(loaded, list) else []
        except (json.JSONDecodeError, OSError):
            notes = []

    action = str((params or {}).get('action') or 'add').strip().lower()
    if action == 'list':
        return {'status': 'liste', 'notes': notes, 'total_notes': len(notes)}

    note = (params or {}).get('message', (params or {}).get('text', ''))
    note = str(note or '').strip()
    if not note:
        return {'status': 'liste', 'notes': notes, 'total_notes': len(notes)}

    notes.append({
        'timestamp': datetime.now().isoformat(),
        'note': note,
    })
    data_dir.write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'status': 'gespeichert', 'note': note, 'total_notes': len(notes)}
