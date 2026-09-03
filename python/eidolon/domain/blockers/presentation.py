from __future__ import annotations


def present_blockers(records):
    result = []
    for item in records:
        result.append({
            'id': item.id,
            'title': item.title,
            'summary': item.summary,
            'category': item.category,
            'status': item.status,
            'requires_user_action': item.requires_user_action,
            'resolution_hint': item.resolution_hint,
            'is_open': item.status == 'open',
        })
    return result
