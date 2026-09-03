"""Notiz-Skill: Merkt Informationen und speichert sie persistent."""
import json
from datetime import datetime

from eidolon.core.config import state_path

def run(params: dict) -> dict:
    note = params.get("message", params.get("text", "Keine Notiz"))
    data_dir = state_path('persistence', 'notes.json')
    data_dir.parent.mkdir(parents=True, exist_ok=True)
    
    notes = []
    if data_dir.exists():
        notes = json.loads(data_dir.read_text())
    
    notes.append({
        "timestamp": datetime.now().isoformat(),
        "note": note
    })
    data_dir.write_text(json.dumps(notes, indent=2))
    
    return {"status": "gespeichert", "note": note, "total_notes": len(notes)}
