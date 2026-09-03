from __future__ import annotations

from typing import Any


def format_topic_clusters(clusters: list[dict[str, Any]], interactions: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    return [
        {
            'cluster_id': f"cluster::{cluster['label'].lower().replace(' ', '-')}",
            'label': cluster['label'],
            'size': cluster['size'],
            'top_terms': cluster.get('top_terms', []),
            'sample_texts': [interactions[idx].get('text', '')[:80] for idx in cluster.get('doc_indices', [])[:3]],
            'source': source,
        }
        for cluster in clusters
    ]
