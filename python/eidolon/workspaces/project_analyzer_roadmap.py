from __future__ import annotations

import re
from pathlib import Path


def parse_roadmap(project_root: Path) -> list[dict]:
    rm = project_root / 'ROADMAP.md'
    if not rm.exists():
        return []
    txt = rm.read_text(encoding='utf-8', errors='replace')
    items = []
    current_phase = None
    for line in txt.splitlines():
        line = line.strip()
        phase_match = re.match(r'^#{1,3}\s*(?:✅|⏳|⬜)?\s*PHASE\s+(.+)$', line, re.IGNORECASE)
        if phase_match:
            current_phase = phase_match.group(1).strip(); continue
        task_match = re.match(r'^[-*]\s+(?:[✅⏳⬜❌]\s+)?(.+)$', line)
        if task_match and current_phase:
            task_text = task_match.group(1).strip()
            status = 'done' if '✅' in line else 'planned' if '⏳' in line else 'idea'
            if task_text and not task_text.startswith('**'):
                items.append({'phase': current_phase, 'title': task_text, 'status': status, 'source': 'roadmap'})
    return items
