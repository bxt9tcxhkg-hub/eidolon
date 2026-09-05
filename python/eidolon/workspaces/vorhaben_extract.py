from __future__ import annotations

import re
from typing import Any

from eidolon.work_context_support import lower_text, normalize_text

_TITLE_PREFIX = re.compile(
    r'^(wir wollen|wir möchten|wir moechten|ich möchte|ich moechte|ich will|bitte|lass uns|lasst uns)\s+',
    re.IGNORECASE,
)
_SENTENCE_SPLIT = re.compile(r'[.!?\n]+')
_NOUNISH = re.compile(r'\b([A-ZÄÖÜ][A-Za-zÄÖÜäöüß]{4,})\b')
_CONSTRAINT = re.compile(
    r'\b((?:mit\s+)?(?:einem?\s+|einer\s+)?eigen(?:em|en|es|e)\s+[A-Za-zÄÖÜäöüß]+|ohne\s+[A-Za-zÄÖÜäöüß]+)\b',
    re.IGNORECASE,
)

VORHABEN_HINTS = (
    'vorhaben', 'wochenende', 'urlaub', 'umzug', 'unterkunft', 'anreise',
    'packen', 'vorbereiten', 'organisieren', 'termin', 'familie', 'treffen',
    'besuch', 'deadline', 'frist', 'buchen', 'buchung', 'reservier',
)

PLAN_SLOTS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ('access', 'Anreise / Zugang', ('anreise', 'anfahren', 'zugang', 'fahrt', 'parken', 'laden', 'abfahrt')),
    ('place', 'Ort / Rahmen', ('unterkunft', 'hotel', 'wohnung', 'ort', 'zimmer', 'raum', 'bad', 'adresse')),
    ('when', 'Dauer / Termine', ('dauer', 'termin', 'wochenende', 'datum', 'uhr', 'frist', 'deadline')),
    ('prepare', 'Vorbereitung', ('packen', 'vorbereit', 'einkauf', 'besorgen', 'checkliste', 'organisieren')),
)

CONSEQUENTIAL_BOOKING = ('buch', 'reserv', 'unterkunft', 'hotel', 'ticket', 'flug')
CONSEQUENTIAL_EXTERNAL = ('anrufen', 'mail schreiben', 'e-mail', 'email', 'extern', 'absenden', 'veröffentlich', 'bestell', 'kaufen', 'zahlen')


def looks_like_vorhaben(message: str) -> bool:
    text = normalize_text(message)
    lowered = lower_text(text)
    if not text or len(text) < 8:
        return False
    if any(hint in lowered for hint in VORHABEN_HINTS):
        return True
    matched = sum(1 for _slot, _title, keys in PLAN_SLOTS if any(key in lowered for key in keys))
    if matched >= 2:
        return True
    organizing = any(token in lowered for token in ('planen', 'organisieren', 'vorbereiten', 'brauchen', 'klären', 'klaeren'))
    return organizing and len(text.split()) >= 4


def extract_title(message: str) -> str:
    text = normalize_text(message)
    if not text:
        return 'Neues Vorhaben'
    first = _SENTENCE_SPLIT.split(text, 1)[0].strip() or text
    if ':' in first:
        left, _right = first.split(':', 1)
        if 0 < len(left.split()) <= 8:
            first = left.strip()
    first = _TITLE_PREFIX.sub('', first).strip(' -–—,')
    nouns = [item for item in _NOUNISH.findall(first) if item.casefold() not in {'wir', 'ich', 'bitte'}]
    if nouns:
        compound = next((item for item in nouns if len(item) >= 10 or item.casefold().endswith(('wochenende', 'urlaub', 'umzug', 'projekt'))), None)
        if compound:
            return compound[:60]
        if len(nouns[0]) >= 6 and len(first.split()) > 8:
            return nouns[0][:60]
    words = first.split()
    title = ' '.join(words[:8]).strip(' -–—,')
    return (title or 'Neues Vorhaben')[:60]


def extract_summary(message: str) -> str:
    text = normalize_text(message)
    return text[:280] if text else ''


def _constraint_note(lowered: str, original: str) -> str:
    match = _CONSTRAINT.search(original)
    if not match:
        return ''
    note = normalize_text(match.group(0))
    if len(note) > 48:
        return ''
    return note


def extract_planning_cards(message: str, *, title: str = '') -> list[dict[str, Any]]:
    text = normalize_text(message)
    lowered = lower_text(text)
    constraint = _constraint_note(lowered, text)
    cards: list[dict[str, Any]] = []
    seen_slots: set[str] = set()

    if title or text:
        cards.append({
            'slot': 'goal',
            'title': title or extract_title(text),
            'description': extract_summary(text) or 'Ziel aus dem Gespräch.',
            'status': 'planned',
        })
        seen_slots.add('goal')

    for slot, default_title, keys in PLAN_SLOTS:
        hits = [key for key in keys if key in lowered]
        if not hits:
            continue
        card_title = default_title
        description = 'Aus dem Vorhaben übernommen.'
        if slot == 'place':
            place_name = 'Unterkunft' if 'unterkunft' in hits else default_title.split(' / ')[0]
            if constraint:
                card_title = f'{place_name} ({constraint})'
                description = constraint
            else:
                card_title = place_name
        elif slot == 'access' and 'laden' in hits:
            card_title = 'Anreise / Laden'
            description = 'Ankunft und Laden aus dem Vorhaben.'
        elif slot == 'when':
            card_title = 'Dauer / Termine'
        elif slot == 'prepare' and 'packen' in hits:
            card_title = 'Packen / Vorbereitung'
            description = 'Vorbereitung aus dem Vorhaben.'
        cards.append({
            'slot': slot,
            'title': card_title,
            'description': description,
            'status': 'planned',
        })
        seen_slots.add(slot)

    if constraint and 'place' not in seen_slots:
        cards.append({
            'slot': 'constraint',
            'title': constraint,
            'description': 'Bedingung aus dem Vorhaben.',
            'status': 'planned',
        })
        seen_slots.add('constraint')

    fallbacks = (
        ('next', 'Nächster Schritt', 'Ersten konkreten Schritt sichtbar machen.'),
        ('open', 'Offene Punkte', 'Was noch geklärt werden muss.'),
        ('prepare', 'Vorbereitung', 'Was vor dem nächsten Schritt bereitliegen muss.'),
    )
    for slot, fallback_title, description in fallbacks:
        if len(cards) >= 3:
            break
        if slot in seen_slots:
            continue
        cards.append({
            'slot': slot,
            'title': fallback_title,
            'description': description,
            'status': 'planned',
        })
        seen_slots.add(slot)
    return cards[:6]


def extract_consequential_approval(message: str) -> dict[str, str] | None:
    lowered = lower_text(message)
    if any(token in lowered for token in CONSEQUENTIAL_BOOKING):
        return {
            'title': 'Buchung vorschlagen',
            'summary': 'Als Nächstes würde ich eine Buchung oder Anfrage nach außen vorschlagen. Das braucht deine Freigabe.',
            'action_type': 'external_write',
        }
    if any(token in lowered for token in CONSEQUENTIAL_EXTERNAL):
        return {
            'title': 'Externe Aktion',
            'summary': 'Der nächste Schritt würde nach außen gehen. Das braucht deine Freigabe.',
            'action_type': 'external_write',
        }
    return None


def extract_vorhaben(message: str) -> dict[str, Any] | None:
    text = normalize_text(message)
    if not text or not looks_like_vorhaben(text):
        return None
    title = extract_title(text)
    summary = extract_summary(text)
    return {
        'title': title,
        'summary': summary,
        'source_message': text,
        'why': 'Du hast ein Vorhaben beschrieben, das mehr als eine einzelne Antwort braucht.',
        'cards': extract_planning_cards(text, title=title),
        'approval': extract_consequential_approval(text),
        'action_relevance': 0.8,
        'recurrence_score': 0.35,
    }
