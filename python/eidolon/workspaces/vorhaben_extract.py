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
_DURATION = re.compile(
    r'\b(\d+\s*(?:nächte|naechte|nights?|tage|tag|stunden|wochen)|nächste\s+woche|naechste\s+woche)\b',
    re.IGNORECASE,
)
_OWN_CONSTRAINT = re.compile(
    r'\b((?:mit\s+)?(?:einem?\s+|einer\s+)?(?:eigen(?:em|en|es|e)|private(?:n|s)?)\s+[A-Za-zÄÖÜäöüß]+)\b',
    re.IGNORECASE,
)
_WITHOUT_CONSTRAINT = re.compile(r'\b(ohne\s+[A-Za-zÄÖÜäöüß]+)\b', re.IGNORECASE)
_NAMED_CONSTRAINT = re.compile(r'\b([A-ZÄÖÜ]{2,4})\b')
_GATE = re.compile(
    r'\b(erst nach(?:\s+[A-Za-zÄÖÜäöüß]+)?|erst wenn|blockiert|wartet auf|ohne freigabe|muss erst|solange nicht)\b',
    re.IGNORECASE,
)
_LIST_SPLIT = re.compile(r'\s*(?:,|;|/|\bund\b)\s*', re.IGNORECASE)

VORHABEN_HINTS = (
    'vorhaben', 'wochenende', 'urlaub', 'umzug', 'unterkunft', 'anreise',
    'packen', 'vorbereiten', 'organisieren', 'termin', 'familie', 'treffen',
    'besuch', 'deadline', 'frist', 'buchen', 'buchung', 'reservier',
    'workshop', 'release', 'agenda', 'changelog',
)

ACCESS_KEYS = (
    'anreise', 'anfahren', 'zugang', 'fahrt', 'parken', 'laden', 'abfahrt',
    'ladesäule', 'ladesaeule', 'tesla', 'auto', 'wagen', 'zug', 'bahn', 'flug',
)
PLACE_KEYS = ('unterkunft', 'hotel', 'wohnung', 'ort', 'zimmer', 'raum', 'bad', 'adresse', 'bath')
LODGING_KEYS = ('unterkunft', 'hotel', 'wohnung', 'bad', 'bath')
TIME_KEYS = ('dauer', 'termin', 'wochenende', 'datum', 'uhr', 'frist', 'deadline', 'zeitraum', 'nächte', 'naechte', 'nights')
PREP_KEYS = ('packen', 'vorbereit', 'einkauf', 'besorgen', 'checkliste', 'organisieren')
OPEN_KEYS = ('klären', 'klaeren', 'offen', 'entscheiden', 'unklar', 'unsicher', 'fehlt')
EVENT_KEYS = ('wochenende', 'urlaub', 'umzug', 'treffen', 'besuch', 'workshop', 'konferenz')
CHARGE_KEYS = ('laden', 'ladesäule', 'ladesaeule', 'tesla')
COMMON_ABBREV = {'AM', 'PM', 'USB', 'PDF', 'URL', 'HTTP', 'HTTPS', 'WWW', 'EUR', 'USD', 'GMT', 'UTC'}
CONSUMED_WORK_STOP = {
    'familienwochenende', 'vorhaben', 'projekt', 'wir', 'ich', 'bitte',
    'anreise', 'laden', 'unterkunft', 'hotel', 'dauer', 'termine', 'packen',
    'vorbereitung', 'tesla', 'auto', 'nächte', 'naechte', 'nights', 'bad',
    'bath', 'cf', 'workshop', 'release',
}

CONSEQUENTIAL_BOOKING = ('buch', 'reserv', 'unterkunft', 'hotel', 'ticket', 'flug')
CONSEQUENTIAL_EXTERNAL = (
    'anrufen', 'mail schreiben', 'e-mail', 'email', 'extern', 'absenden',
    'veröffentlich', 'bestell', 'kaufen', 'zahlen',
)


def looks_like_vorhaben(message: str) -> bool:
    text = normalize_text(message)
    lowered = lower_text(text)
    if not text or len(text) < 8:
        return False
    if any(hint in lowered for hint in VORHABEN_HINTS):
        return True
    facet_hits = sum(
        1
        for keys in (ACCESS_KEYS, PLACE_KEYS, TIME_KEYS, PREP_KEYS)
        if any(key in lowered for key in keys)
    )
    if facet_hits >= 2:
        return True
    organizing = any(
        token in lowered
        for token in ('planen', 'organisieren', 'vorbereiten', 'brauchen', 'klären', 'klaeren', 'bauen', 'implement')
    )
    return organizing and len(text.split()) >= 4


_LEAD_SPLIT = re.compile(r'\s+(?:mit|und|ohne)\s+', re.IGNORECASE)
_HYPHEN_TITLE = re.compile(r'^[A-ZÄÖÜ][A-Za-zÄÖÜäöüß0-9]+(?:-[A-Za-zÄÖÜäöüß0-9]+)+$')


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
    lead = _LEAD_SPLIT.split(first, 1)[0].strip(' -–—,') or first
    first_token = lead.split()[0] if lead.split() else ''
    if _HYPHEN_TITLE.match(first_token):
        return first_token[:60]
    nouns = [item for item in _NOUNISH.findall(lead) if item.casefold() not in {'wir', 'ich', 'bitte'}]
    if nouns:
        compound = next(
            (
                item
                for item in nouns
                if len(item) >= 10 or item.casefold().endswith(('wochenende', 'urlaub', 'umzug', 'projekt', 'workshop'))
            ),
            None,
        )
        if compound:
            return compound[:60]
        if len(nouns[0]) >= 6 and len(lead.split()) > 6:
            return nouns[0][:60]
    words = lead.split()
    title = ' '.join(words[:8]).strip(' -–—,')
    return (title or 'Neues Vorhaben')[:60]


def extract_summary(message: str) -> str:
    text = normalize_text(message)
    return text[:280] if text else ''


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = normalize_text(item)
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        result.append(text)
    return result


def _hits(lowered: str, keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if key in lowered]


def _named_constraints(original: str) -> list[str]:
    found: list[str] = []
    for match in _NAMED_CONSTRAINT.finditer(original):
        token = match.group(1)
        if token in COMMON_ABBREV:
            continue
        if token.casefold() in {'ich', 'wir'}:
            continue
        found.append(token)
    return _unique(found)


_TRAILING_VERBS = {
    'klären', 'klaeren', 'vorbereiten', 'bauen', 'organisieren', 'besorgen',
    'packen', 'entscheiden',
}
_MIT_SKIP = ('eigen', 'einem', 'einer', 'eine', 'einem', 'private', 'privaten')
_LIST_PLACE_OK = {'raum', 'zimmer', 'ort', 'adresse'}


def _list_source(text: str) -> str:
    if ':' not in text:
        return ''
    tail = text.split(':', 1)[1].strip()
    return (_SENTENCE_SPLIT.split(tail, 1)[0] or tail).strip()


def _strip_trailing_verbs(phrase: str) -> str:
    words = phrase.split()
    while words and words[-1].casefold().strip(' .') in _TRAILING_VERBS:
        words.pop()
    return ' '.join(words).strip(' -–—,.')


def _list_items(text: str) -> list[str]:
    parts = [part.strip(' .') for part in _LIST_SPLIT.split(text) if part.strip(' .')]
    cleaned: list[str] = []
    for part in parts:
        words = [
            word
            for word in part.split()
            if word.casefold() not in {'mit', 'und', 'den', 'die', 'das', 'ein', 'eine', 'der'}
        ]
        phrase = _strip_trailing_verbs(' '.join(words).strip(' -–—,'))
        if phrase:
            cleaned.append(phrase)
    return cleaned


def _work_items(text: str, consumed: set[str], *, lodging: bool) -> list[str]:
    items: list[str] = []
    source = _list_source(text)
    if source:
        items.extend(_list_items(source))
    for match in re.finditer(r'\bmit\s+([A-Za-zÄÖÜäöüß0-9]+(?:\s+und\s+[A-Za-zÄÖÜäöüß0-9]+)*)', text, flags=re.IGNORECASE):
        bit = match.group(1)
        if bit.casefold().startswith(_MIT_SKIP):
            continue
        items.extend(_list_items(bit))
    blocked_facets = set(ACCESS_KEYS + TIME_KEYS + PREP_KEYS + LODGING_KEYS)
    if lodging:
        blocked_facets.update(PLACE_KEYS)
    else:
        blocked_facets.update(set(PLACE_KEYS) - _LIST_PLACE_OK)
    result: list[str] = []
    for item in items:
        key = item.casefold()
        words = set(key.split())
        if key in consumed or key in CONSUMED_WORK_STOP:
            continue
        if words & (consumed | CONSUMED_WORK_STOP | blocked_facets):
            continue
        if _DURATION.search(item) or _OWN_CONSTRAINT.search(item) or _WITHOUT_CONSTRAINT.search(item):
            continue
        if len(item.split()) > 6 or len(key) < 3:
            continue
        result.append(item)
    return _unique(result)


def extract_facts(message: str) -> dict[str, Any]:
    text = normalize_text(message)
    lowered = lower_text(text)
    durations = _unique(match.group(0) for match in _DURATION.finditer(text))
    constraints = _unique(
        [match.group(0) for match in _OWN_CONSTRAINT.finditer(text)]
        + [match.group(0) for match in _WITHOUT_CONSTRAINT.finditer(text)]
    )
    named = _named_constraints(text)
    access = _hits(lowered, ACCESS_KEYS)
    place = _hits(lowered, PLACE_KEYS)
    time = _hits(lowered, TIME_KEYS)
    prep = _hits(lowered, PREP_KEYS)
    open_hits = _hits(lowered, OPEN_KEYS)
    gates = _unique(match.group(0) for match in _GATE.finditer(text))
    event_like = any(key in lowered for key in EVENT_KEYS)
    lodging = any(key in place for key in LODGING_KEYS)
    consumed = {item.casefold() for item in durations + constraints + named + access}
    if lodging:
        consumed.update(place)
    else:
        consumed.update(item for item in place if item not in _LIST_PLACE_OK)
    if extract_title(text):
        consumed.add(extract_title(text).casefold())
    return {
        'text': text,
        'lowered': lowered,
        'durations': durations,
        'constraints': constraints,
        'named_constraints': named,
        'access': access,
        'place': place,
        'time': time,
        'prep': prep,
        'open': open_hits,
        'gates': gates,
        'event_like': event_like,
        'lodging': lodging,
        'work_items': _work_items(text, consumed, lodging=lodging),
    }


def _join_notes(*groups: list[str] | str) -> str:
    parts: list[str] = []
    for group in groups:
        if isinstance(group, str):
            if group.strip():
                parts.append(group.strip())
            continue
        parts.extend(item for item in group if str(item).strip())
    return ' · '.join(_unique(parts))


def _card(
    slot: str,
    title: str,
    *,
    notes: str = '',
    status: str = 'planned',
    constraints: list[str] | None = None,
    facts: list[str] | None = None,
) -> dict[str, Any]:
    fact_list = _unique(facts or [])
    constraint_list = _unique(constraints or [])
    description = notes[:180]
    return {
        'slot': slot,
        'title': title[:80],
        'description': description,
        'subtitle': description,
        'status': status if status in {'planned', 'blocked', 'in_progress', 'idea', 'done'} else 'planned',
        'constraints': constraint_list,
        'facts': fact_list,
        'metadata': {
            'slot': slot,
            'seed': 'vorhaben',
            'facts': fact_list,
            'constraints': constraint_list,
        },
    }


def _place_title(facts: dict[str, Any]) -> str:
    place = set(facts['place'])
    bath = next((item for item in facts['constraints'] if 'bad' in item.casefold() or 'bath' in item.casefold()), '')
    if 'unterkunft' in place or 'hotel' in place:
        base = 'Unterkunft'
    elif 'wohnung' in place:
        base = 'Wohnung'
    elif 'zimmer' in place:
        base = 'Zimmer'
    elif 'raum' in place:
        base = 'Raum'
    elif bath:
        base = 'Unterkunft'
    else:
        base = 'Ort'
    if bath:
        return f'{base} mit eigenem Bad' if 'bad' in bath.casefold() or 'bath' in bath.casefold() else f'{base} ({bath})'
    own = next((item for item in facts['constraints'] if item.casefold().startswith(('eigen', 'mit eigen', 'private'))), '')
    if own:
        return f'{base} ({own})'
    return base


def _access_title(facts: dict[str, Any]) -> str:
    cues = set(facts['access'])
    if cues & set(CHARGE_KEYS) or 'laden' in facts['lowered']:
        return 'Anreise & Laden'
    if 'anreise' in cues:
        return 'Anreise'
    return 'Anreise / Zugang'


def _blocked_for(title: str, facts: dict[str, Any]) -> bool:
    if not facts['gates']:
        return False
    lowered_title = title.casefold()
    for gate in facts['gates']:
        tail = lower_text(gate.replace('erst nach', '').replace('erst wenn', ''))
        if tail and tail in lowered_title:
            return True
        if tail and any(tail in lower_text(item) for item in facts['work_items'] if item.casefold() == lowered_title):
            return True
    return any(lowered_title in lower_text(gate) or lower_text(gate) in lowered_title for gate in facts['gates'])


def extract_planning_cards(message: str, *, title: str = '') -> list[dict[str, Any]]:
    facts = extract_facts(message)
    heading = title or extract_title(facts['text'])
    cards: list[dict[str, Any]] = []
    seen_slots: set[str] = set()
    seen_titles: set[str] = set()

    def add(card: dict[str, Any]) -> None:
        key = card['title'].casefold()
        if not card['title'] or card['slot'] in seen_slots or key in seen_titles:
            return
        if heading and key == heading.casefold() and card['slot'] != 'goal':
            return
        cards.append(card)
        seen_slots.add(card['slot'])
        seen_titles.add(key)

    lodging_constraints = [
        item
        for item in facts['constraints'] + facts['named_constraints']
        if any(token in item.casefold() for token in ('bad', 'bath', 'zimmer', 'unterkunft'))
        or (facts['lodging'] and item in facts['named_constraints'])
    ]
    access_facts = [item for item in facts['access'] if item in {'tesla', 'auto', 'wagen', 'zug', 'bahn', 'flug'}]
    if 'tesla' in facts['access']:
        access_facts = _unique(['Tesla'] + access_facts)

    if facts['access']:
        access_title = _access_title(facts)
        add(_card(
            'access',
            access_title,
            notes=_join_notes(access_facts, [item for item in facts['access'] if item in {'laden', 'parken', 'anreise'}]),
            facts=access_facts or facts['access'],
        ))

    if facts['lodging'] or (facts['place'] and any(key in facts['place'] for key in LODGING_KEYS)):
        place_title = _place_title(facts)
        add(_card(
            'place',
            place_title,
            notes=_join_notes(facts['constraints'], lodging_constraints),
            constraints=facts['constraints'] + lodging_constraints,
            facts=facts['place'],
        ))
    elif facts['place'] and not facts['work_items']:
        add(_card('place', _place_title(facts), notes=_join_notes(facts['constraints']), constraints=facts['constraints'], facts=facts['place']))

    if facts['durations'] or facts['time']:
        time_notes = facts['durations'] or [item for item in ('Dauer', 'Termin', 'Wochenende', 'Deadline', 'Frist') if item.casefold() in facts['lowered']]
        add(_card(
            'when',
            'Zeitraum',
            notes=_join_notes(time_notes),
            facts=facts['durations'] or facts['time'],
        ))

    want_prep = (
        (bool(facts['prep']) and len(facts['work_items']) < 3)
        or (facts['event_like'] and (facts['access'] or facts['lodging']) and len(facts['work_items']) < 3)
    )
    if want_prep:
        prep_title = 'Packen/Vorbereitung' if ('packen' in facts['prep'] or facts['event_like']) else 'Vorbereitung'
        add(_card('prepare', prep_title, notes=_join_notes(facts['prep']), facts=facts['prep']))

    for index, item in enumerate(facts['work_items'][:4]):
        status = 'blocked' if _blocked_for(item, facts) else 'planned'
        add(_card(f'work_{index}', item, notes='', status=status, facts=[item]))

    open_bits = facts['named_constraints'] + facts['open']
    if 'klären' in facts['lowered'] or 'klaeren' in facts['lowered']:
        if facts['durations'] or facts['time']:
            open_bits.append('Zeitraum noch klären' if 'klären' in facts['lowered'] or 'klaeren' in facts['lowered'] else '')
    if facts['named_constraints'] or facts['open'] or (want_prep and facts['named_constraints']):
        add(_card(
            'open',
            'Offene Entscheidungen',
            notes=_join_notes(facts['named_constraints'], facts['open']),
            constraints=facts['named_constraints'],
            facts=facts['open'] or facts['named_constraints'],
            status='blocked' if facts['gates'] and not any(card['status'] == 'blocked' for card in cards) and any('freigabe' in gate.casefold() for gate in facts['gates']) else 'planned',
        ))

    if len(cards) < 3 and heading:
        add(_card('goal', heading, notes=extract_summary(facts['text']) or 'Ziel aus dem Gespräch.', facts=[heading]))

    if facts['constraints'] and not any(card['constraints'] for card in cards):
        add(_card(
            'constraint',
            facts['constraints'][0],
            notes='Bedingung aus dem Vorhaben.',
            constraints=facts['constraints'],
        ))

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
        'facts': extract_facts(text),
    }
