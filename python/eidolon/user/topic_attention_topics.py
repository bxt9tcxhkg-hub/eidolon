from __future__ import annotations

from collections import Counter

from eidolon.user.topic_attention_extractors import classify_needs, extract_candidate_phrases, semantic_labels, suggest_workspace

EMPTY_NEEDS = {
    'planning': 0.0,
    'tracking': 0.0,
    'decision': 0.0,
    'knowledge': 0.0,
    'execution': 0.0,
    'reflection': 0.0,
}


def _topic_entry(label: str) -> dict:
    return {
        'topic_id': f"topic:{label.lower().replace(' ', '-')}",
        'label': label,
        'mentions': 0,
        'docs': 0,
        'sources': Counter(),
        'needs_raw': dict(EMPTY_NEEDS),
        'entities': Counter(),
    }


def extract_topics(interactions: list[dict]) -> list[dict]:
    total = max(len(interactions), 1)
    topic_stats: dict[str, dict] = {}
    for item in interactions:
        text = str(item.get('text') or '')
        needs = classify_needs(text.lower())
        labels = semantic_labels(text)
        if not labels:
            continue
        phrases = extract_candidate_phrases(text)
        seen: set[str] = set()
        for label in labels:
            if not label or label in seen:
                continue
            seen.add(label)
            entry = topic_stats.setdefault(label, _topic_entry(label))
            entry['mentions'] += 1
            entry['docs'] += 1
            entry['sources'][str(item.get('source') or 'unknown')] += 1
            for key, value in needs.items():
                entry['needs_raw'][key] += value
            for phrase in phrases[:5]:
                entry['entities'][phrase] += 1
    topics = []
    for label, entry in sorted(topic_stats.items(), key=lambda item: item[1]['mentions'], reverse=True)[:8]:
        needs = {key: round(value / max(1, entry['docs']), 3) for key, value in entry['needs_raw'].items()}
        topics.append({
            'topic_id': entry['topic_id'],
            'label': label,
            'recurrence_score': round(entry['mentions'] / total, 3),
            'freshness_score': round(min(1.0, entry['docs'] / total), 3),
            'action_relevance': round(min(1.0, (needs['planning'] + needs['execution'] + needs['decision'] + needs['tracking']) / 2.5), 3),
            'needs': needs,
            'entities': [phrase for phrase, _count in entry['entities'].most_common(4)],
            'workspace_suggestion': suggest_workspace(needs),
            'signal_count': entry['mentions'],
            'source_breakdown': dict(entry['sources']),
            'is_live_context': True,
        })
    return topics
