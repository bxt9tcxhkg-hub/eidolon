"""Topic Attention Store — erweitert um semantisches Clustering."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

from eidolon.core.config import state_path
from eidolon.user.semantic_clustering import get_semantic_clusterer
from eidolon.user.topic_attention_analysis import extract_topics
from eidolon.user.topic_attention_sources import is_live_context_source


class TopicAttentionStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('user', 'topic_attention.json', project_root=self.project_root)
        self.interactions_path = state_path('user', 'interaction_log.jsonl', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {'topics': [], 'updated_at': None}
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return {'topics': [], 'updated_at': None}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def record_interaction(self, text: str, source: str = 'chat') -> None:
        payload = {'timestamp': datetime.now(timezone.utc).isoformat(), 'source': source, 'text': str(text or '').strip()}
        with self.interactions_path.open('a', encoding='utf-8') as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + '\n')

    def _read_interactions(self, limit: int = 200) -> list[dict[str, Any]]:
        if not self.interactions_path.exists():
            return []
        result: list[dict[str, Any]] = []
        for line in self.interactions_path.read_text(encoding='utf-8').splitlines()[-limit:]:
            try:
                result.append(json.loads(line))
            except Exception:
                continue
        return result

    def read_live_interactions(self, limit: int = 200) -> list[dict[str, Any]]:
        return [item for item in self._read_interactions(limit) if is_live_context_source(item.get('source'))]

    async def recompute_semantic(self) -> dict[str, Any]:
        interactions = self.read_live_interactions()
        topics = extract_topics(interactions)
        try:
            clusterer = get_semantic_clusterer(self.project_root)
            clusters = await clusterer.cluster_interactions(interactions)
            for topic in topics:
                matches = [cluster for cluster in clusters if any(term.lower() in topic['label'].lower() for term in cluster.get('top_terms', []))]
                if matches:
                    best = max(matches, key=lambda cluster: cluster.get('size', 0))
                    topic['semantic_source'] = best.get('source', 'tfidf')
                    topic['semantic_size'] = best.get('size', 1)
                    topic['cluster_terms'] = best.get('top_terms', [])
        except Exception:
            pass
        payload = {
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'topics': topics,
            'interaction_count': len(interactions),
            'live_context_only': True,
            'semantic_clustering': True,
        }
        self._save(payload)
        return payload

    def recompute(self) -> dict[str, Any]:
        interactions = self.read_live_interactions()
        payload = {
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'topics': extract_topics(interactions),
            'interaction_count': len(interactions),
            'live_context_only': True,
        }
        self._save(payload)
        return payload

    def snapshot(self) -> dict[str, Any]:
        data = self._load()
        return self.recompute() if not data.get('updated_at') else data
