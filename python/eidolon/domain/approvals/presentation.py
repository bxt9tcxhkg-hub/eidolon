from __future__ import annotations


def present_approvals(records):
    result = []
    for item in records:
        result.append({
            'id': item.id,
            'title': item.title,
            'summary': item.summary,
            'action_type': item.action_type,
            'status': item.status,
            'requested_at': item.requested_at,
            'resolved_at': item.resolved_at,
            'resolved_by': item.resolved_by,
            'is_pending': item.status == 'pending',
            'requires_decision': item.status == 'pending',
        })
    return result
