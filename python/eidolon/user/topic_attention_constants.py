from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß0-9_-]{2,}")
STOPWORDS = {
    'und', 'oder', 'aber', 'dass', 'wenn', 'weil', 'nicht', 'noch', 'auch', 'wieder', 'über', 'eine', 'einen', 'einer',
    'einem', 'dieser', 'dieses', 'diese', 'der', 'die', 'das', 'mit', 'für', 'auf', 'von', 'ist', 'sind', 'ich', 'wir',
    'du', 'er', 'sie', 'es', 'man', 'mir', 'mich', 'mein', 'dein', 'sein', 'ihr', 'uns', 'euch', 'wie', 'was', 'warum',
    'wird', 'werden', 'haben', 'hast', 'hat', 'schon', 'sehr', 'mehr', 'nur', 'einer', 'einem', 'eines', 'thema',
    'hilfe', 'bereich', 'soll', 'sollen', 'kann', 'könnte', 'darf', 'bitte', 'mach', 'machen', 'user', 'nutzer', 'eidolon',
    'will', 'hilf', 'helfen', 'nächste', 'schritte', 'sehen', 'zeigen', 'bauen', 'strukturieren', 'vergleichen',
}
SEMANTIC_PATTERNS: dict[str, tuple[str, ...]] = {
    'Training': ('training', 'trainieren', 'workout', 'regeneration', 'übung', 'muskelaufbau', 'session'),
    'Projektplanung': ('projekt', 'roadmap', 'milestone', 'task', 'abhängigkeit', 'board', 'graph'),
    'Lernen': ('lernen', 'studium', 'üben', 'kurs', 'wissen', 'sprache'),
    'Gesundheit': ('gesundheit', 'schlaf', 'stress', 'energie', 'regeneration', 'symptom'),
    'Finanzen': ('budget', 'sparen', 'kosten', 'ausgabe', 'finanz', 'anschaffung'),
    'Karriere': ('bewerbung', 'lebenslauf', 'rolle', 'job', 'karriere', 'interview'),
    'Forschung': ('research', 'forschung', 'quelle', 'paper', 'hypothese', 'analyse'),
    'Wohnen': ('wohnung', 'umzug', 'miete', 'haus', 'besichtigung', 'immobilie'),
}
WORKSPACE_BY_NEED = {
    'planning': 'planner_workspace',
    'tracking': 'tracker_workspace',
    'decision': 'decision_workspace',
    'knowledge': 'knowledge_workspace',
    'execution': 'project_workspace',
    'reflection': 'review_workspace',
}
