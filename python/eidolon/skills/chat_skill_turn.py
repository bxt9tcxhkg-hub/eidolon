"""Conservative skill matching for the everyday chat turn.

Casual talk, settings, and runtime-truth questions stay on their own paths.
A match either runs a live handler or says the catalog entry is not wired.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from eidolon.skills.live_skills import (
    CATALOG_SKILL_IDS,
    LIVE_SKILL_IDS,
    execute_live_skill,
    format_live_skill_reply,
    is_live_skill,
    unwired_skill_reply,
)

_LIVE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ('system_info', (
        r'\bsysteminfo\b',
        r'\bsystem-info\b',
        r'\bsystem_info\b',
        r'\bsystem info\b',
        r'\bsysteminformationen?\b',
        r'\bsystem-informationen?\b',
        r'\bhostdaten\b',
        r'\bhostname\b',
        r'\bcpu[- ]?(?:auslastung|last|prozent)\b',
        r'\bspeicherauslastung\b',
        r'\bbetriebssystem\b',
    )),
    ('device_status', (
        r'\bgeräte[- ]?status\b',
        r'\bgeraete[- ]?status\b',
        r'\bdevice[-_ ]?status\b',
        r'\bverbundene geräte\b',
        r'\bverbundene geraete\b',
        r'\bwelche geräte\b',
        r'\bwelche geraete\b',
        r'\bgekoppelte geräte\b',
        r'\bgekoppelte geraete\b',
        r'\bmesh-geräte\b',
        r'\bmesh-geraete\b',
    )),
    ('note', (
        r'\bnotizen?\b',
        r'\bnotiere\b',
        r'\bmerke dir\b',
        r'\bspeichere notiz\b',
        r'\bneue notiz\b',
    )),
)

_UNWIRED_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ('calendar', (
        r'\bkalender\b',
        r'\bcalendar-summarize\b',
        r'\bcalendar_summarize\b',
        r'\bcalendar summarize\b',
        r'\bim kalender\b',
    )),
    ('file_organizer', (
        r'\bdateien organisier',
        r'\bfile[-_ ]?organizer\b',
    )),
    ('mesh_send', (
        r'\bmesh[-_ ]?send\b',
        r'\bsende mesh\b',
        r'\bmesh-nachricht\b',
        r'\bmesh nachricht\b',
    )),
    ('goal_manager', (
        r'\bgoal[-_ ]?manager\b',
    )),
    ('skill-generator', (
        r'\bskill[-_ ]?generator\b',
    )),
    ('runtime_facts', (
        r'\bruntime[-_ ]?facts\b',
        r'\bruntime[-_ ]?fakten\b',
    )),
)

_NOTE_LIST_MARKERS = (
    'zeige notiz', 'zeig notiz', 'liste notiz', 'welche notiz',
    'meine notizen', 'notizen anzeigen', 'notizen zeigen',
)

_NOTE_PREFIX = re.compile(
    r'^(bitte\s+)?(notiere|notiz:|notiz\s+|merke dir(?:\s+als\s+notiz)?|speichere notiz|neue notiz)\s*',
    re.IGNORECASE,
)


@dataclass
class SkillTurnMatch:
    name: str
    wired: bool
    payload: dict[str, Any] = field(default_factory=dict)
    reason: str = ''


@dataclass
class SkillTurnResult:
    name: str
    wired: bool
    executed: bool
    ok: bool
    reply: str
    outcome: dict[str, Any] = field(default_factory=dict)
    disabled: bool = False


def _first_pattern(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def match_chat_skill(message: str) -> SkillTurnMatch | None:
    text = str(message or '').strip()
    if not text:
        return None
    lowered = text.casefold()
    for name, patterns in _LIVE_PATTERNS:
        if _first_pattern(lowered, patterns):
            payload = _payload_for(name, text, lowered)
            return SkillTurnMatch(name=name, wired=True, payload=payload, reason='live_handler')
    for name, patterns in _UNWIRED_PATTERNS:
        if _first_pattern(lowered, patterns):
            return SkillTurnMatch(name=name, wired=False, payload={}, reason='catalog_only')
    return None


def _payload_for(name: str, text: str, lowered: str) -> dict[str, Any]:
    if name != 'note':
        return {}
    if any(marker in lowered for marker in _NOTE_LIST_MARKERS):
        return {'action': 'list'}
    content = _NOTE_PREFIX.sub('', text).strip()
    if not content or content.casefold() in {'notiz', 'notizen'}:
        return {'action': 'list'}
    return {'action': 'add', 'text': content, 'message': content}


def _skill_enabled(name: str, enabled_lookup: Callable[[str], bool] | None) -> bool:
    if enabled_lookup is None:
        return True
    try:
        return bool(enabled_lookup(name))
    except Exception:
        return True


def run_chat_skill_turn(
    message: str,
    *,
    enabled_lookup: Callable[[str], bool] | None = None,
) -> SkillTurnResult | None:
    match = match_chat_skill(message)
    if match is None:
        return None
    if not match.wired or not is_live_skill(match.name):
        return SkillTurnResult(
            name=match.name,
            wired=False,
            executed=False,
            ok=False,
            reply=unwired_skill_reply(match.name),
            outcome={'ok': False, 'wired': False, 'executed': False, 'skill': match.name},
        )
    if not _skill_enabled(match.name, enabled_lookup):
        return SkillTurnResult(
            name=match.name,
            wired=True,
            executed=False,
            ok=False,
            disabled=True,
            reply=(
                f'Der Skill „{match.name}“ ist ausgeschaltet. '
                'Unter Mehr → Fähigkeiten-Katalog kannst du ihn wieder einschalten. Ich führe ihn nicht aus.'
            ),
            outcome={'ok': False, 'wired': True, 'executed': False, 'skill': match.name, 'enabled': False},
        )
    outcome = execute_live_skill(match.name, match.payload)
    return SkillTurnResult(
        name=match.name,
        wired=True,
        executed=bool(outcome.get('executed')),
        ok=bool(outcome.get('ok')),
        reply=format_live_skill_reply(match.name, outcome),
        outcome=outcome,
    )


def catalog_flags(name: str) -> dict[str, bool]:
    live = is_live_skill(name)
    return {
        'executable': live,
        'runtime_wired': live,
        'catalog_only': name in CATALOG_SKILL_IDS or not live,
    }


def live_skill_names() -> list[str]:
    return sorted(LIVE_SKILL_IDS)
