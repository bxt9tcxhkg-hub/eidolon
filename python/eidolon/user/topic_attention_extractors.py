from __future__ import annotations

from eidolon.user.topic_attention_constants import SEMANTIC_PATTERNS, STOPWORDS, TOKEN_RE, WORKSPACE_BY_NEED


def extract_candidate_phrases(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    filtered = [token for token in tokens if token not in STOPWORDS]
    return [f'{filtered[index]} {filtered[index + 1]}' for index in range(len(filtered) - 1) if filtered[index] != filtered[index + 1]]


def classify_needs(lowered: str) -> dict[str, float]:
    return {
        'planning': 1.0 if any(keyword in lowered for keyword in ('plan', 'schritt', 'roadmap', 'woche', 'phase', 'struktur')) else 0.0,
        'tracking': 1.0 if any(keyword in lowered for keyword in ('fortschritt', 'track', 'verlauf', 'heute', 'session', 'historie')) else 0.0,
        'decision': 1.0 if any(keyword in lowered for keyword in ('oder', 'vs', 'vergleich', 'entscheiden', 'option', 'abwägen')) else 0.0,
        'knowledge': 1.0 if any(keyword in lowered for keyword in ('warum', 'wie', 'erkläre', 'verstehen', 'wissen', 'frage')) else 0.0,
        'execution': 1.0 if any(keyword in lowered for keyword in ('mach', 'umsetzen', 'fix', 'reparier', 'erstellen', 'bauen')) else 0.0,
        'reflection': 1.0 if any(keyword in lowered for keyword in ('denke', 'fühle', 'beschäftigt', 'reflekt', 'stress', 'belastet')) else 0.0,
    }


def semantic_labels(text: str) -> list[str]:
    lowered = text.lower()
    return [label for label, patterns in SEMANTIC_PATTERNS.items() if any(pattern in lowered for pattern in patterns)]


def suggest_workspace(needs: dict[str, float]) -> str:
    ranked = sorted((needs or {}).items(), key=lambda item: item[1], reverse=True)
    top = ranked[0][0] if ranked and ranked[0][1] > 0 else 'knowledge'
    return WORKSPACE_BY_NEED.get(top, 'mixed_workspace')
