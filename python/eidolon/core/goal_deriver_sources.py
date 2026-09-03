from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from eidolon.core.goal_deriver_keys import KEY_CAP_PREFIX, KEY_ROADMAP_PREFIX, KEY_RUST_STUBS

_CAP_IN_TEXT = re.compile(r'`([a-z_]+\.[a-z_]+)`')


def from_roadmap(project_root: Path) -> list[dict[str, Any]]:
    roadmap = Path(project_root) / 'ROADMAP.md'
    if not roadmap.exists():
        return []
    text = roadmap.read_text(encoding='utf-8', errors='replace')
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip().lstrip('-*| ').strip()
        if not (12 < len(line) < 240):
            continue
        has_blocker = '❌' in line
        has_partial = '⚠️' in line or '⚠' in line
        if not (has_blocker or has_partial):
            continue
        title = re.split(r'[❌⚠(]', line)[0].replace('✅', '').replace('/', ' ').strip(' `*:—–-')
        title = re.sub(r'\s{2,}', ' ', title)
        if len(title) < 6 or title.lower() in seen:
            continue
        seen.add(title.lower())
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower())[:40].strip('-')
        cap_match = _CAP_IN_TEXT.search(line)
        problem_key = f"{KEY_CAP_PREFIX}{cap_match.group(1)}" if cap_match else f'{KEY_ROADMAP_PREFIX}{slug}'
        out.append({
            'problem_key': problem_key,
            'title': f"{'Blocker' if has_blocker else 'Härten'}: {title}"[:110],
            'description': line[:400],
            'category': 'development',
            'priority': 4 if has_blocker else 2,
            'source': f'ROADMAP.md#{slug}',
            'evidence': line[:200],
            'steps': ['Ursache analysieren', 'Umsetzen', 'In ROADMAP als erledigt markieren'] if has_blocker else ['Aktuellen Reifegrad prüfen', 'Lücke schließen', 'End-to-End verifizieren'],
        })
        if len(out) >= 8:
            break
    return out


def verify_roadmap(project_root: Path, slug: str) -> tuple[bool, str]:
    roadmap = Path(project_root) / 'ROADMAP.md'
    if not roadmap.exists():
        return False, 'ROADMAP.md nicht vorhanden'
    text = roadmap.read_text(encoding='utf-8', errors='replace')
    for raw in text.splitlines():
        line = raw.strip().lstrip('-*| ').strip()
        title = re.split(r'[❌⚠(]', line)[0].replace('✅', '').replace('/', ' ').strip(' `*:—–-')
        title = re.sub(r'\s{2,}', ' ', title)
        if re.sub(r'[^a-z0-9]+', '-', title.lower())[:40].strip('-') == slug:
            if '❌' in line or '⚠️' in line or '⚠' in line:
                return True, line[:150]
            return False, f'Marker in ROADMAP entfernt: {line[:110]}'
    return False, f"Zeile '{slug}' nicht mehr in ROADMAP.md gefunden"


def scan_rust_stubs(project_root: Path) -> tuple[list[str], int]:
    crates = Path(project_root) / 'crates'
    if not crates.exists():
        return [], 0
    stubs: list[str] = []
    total = 0
    for rs in crates.rglob('*.rs'):
        total += 1
        try:
            body = rs.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        if len(body.strip()) < 200 and 'impl' not in body:
            stubs.append(str(rs.relative_to(project_root)))
    return stubs, total


def from_rust_stubs(project_root: Path) -> list[dict[str, Any]]:
    stubs, total = scan_rust_stubs(project_root)
    if not stubs:
        return []
    return [{
        'problem_key': KEY_RUST_STUBS,
        'title': f'Rust-Stubs ausbauen ({len(stubs)} von {total} Dateien)',
        'description': f"{len(stubs)} .rs-Dateien enthalten unter 200 Zeichen und keine impl-Blöcke. Betroffen u.a.: {', '.join(stubs[:4])}",
        'category': 'development',
        'priority': 2,
        'source': 'crates/**/*.rs',
        'evidence': f'{len(stubs)}/{total} Dateien sind Stubs',
        'steps': [f'Implementieren: {stub}' for stub in stubs[:5]],
    }]


def verify_rust_stubs(project_root: Path) -> tuple[bool, str]:
    stubs, total = scan_rust_stubs(project_root)
    if stubs:
        return True, f'{len(stubs)}/{total} Dateien sind Stubs'
    return False, f'Keine Stubs mehr ({total} Dateien geprüft)'
