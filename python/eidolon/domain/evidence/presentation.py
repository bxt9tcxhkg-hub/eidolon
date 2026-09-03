from __future__ import annotations


def present_evidence(records):
    result = []
    for item in records:
        result.append({
            'id': item.id,
            'owner_type': item.owner_type,
            'owner_id': item.owner_id,
            'kind': item.kind,
            'title': item.title,
            'summary': item.summary,
            'artifact_ref': item.artifact_ref,
            'metadata': item.metadata_json,
            'created_at': item.created_at,
            'evidence_status': 'observed',
        })
    return result
