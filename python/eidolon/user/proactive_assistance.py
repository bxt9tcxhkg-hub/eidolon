from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

from eidolon.core.config import state_path
from eidolon.user.proactive_policy import cooldown_for_status, policy_limits, suggestion_id, under_cooldown
from eidolon.user.proactive_scoring import assistance_mode, message_for, priority_score, urgency
from eidolon.user.proactive_visibility import has_active_workspace, should_surface


class ProactiveAssistanceStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('user', 'proactive_assistance.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {'suggestions': [], 'updated_at': None}
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return {'suggestions': [], 'updated_at': None}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def snapshot(self) -> dict[str, Any]:
        data = self._load()
        if not self.path.exists():
            self._save(data)
        return data

    def generate(self, topics: list[dict[str, Any]], workspaces: list[dict[str, Any]], user_model: dict[str, Any]) -> dict[str, Any]:
        previous = {item['suggestion_id']: item for item in self.snapshot().get('suggestions', [])}
        suggestions = []
        max_visible, allow_visible = policy_limits(user_model)
        active_workspace_exists = has_active_workspace(workspaces)
        for topic in topics[:5]:
            if not topic.get('is_live_context'):
                continue
            score = float(topic.get('recurrence_score', 0)) + float(topic.get('action_relevance', 0))
            if score < 0.65:
                continue
            sid = suggestion_id(topic['topic_id'])
            prior = previous.get(sid, {})
            status = str(prior.get('status') or 'new')
            cooldown_minutes = cooldown_for_status(status)
            if status in {'dismissed', 'ignored', 'unhelpful'} and under_cooldown(prior, cooldown_minutes):
                continue
            workspace = next((w for w in workspaces if w.get('metadata', {}).get('topic_id') == topic.get('topic_id')), None)
            top_needs = sorted((topic.get('needs') or {}).items(), key=lambda kv: kv[1], reverse=True)[:2]
            needs_text = ', '.join(name for name, value in top_needs if value > 0) or 'Struktur'
            mode = assistance_mode(topic, workspace)
            urgency_value = urgency(topic)
            suggestions.append({'suggestion_id': sid, 'topic_id': topic['topic_id'], 'topic_label': topic['label'], 'workspace_id': workspace.get('workspace_id') if workspace else None, 'workspace_state': workspace.get('state') if workspace else None, 'workspace_type': workspace.get('workspace_type') if workspace else topic.get('workspace_suggestion'), 'confidence': round(min(1.0, score / 1.8), 3), 'priority_score': priority_score(topic, workspace, mode, urgency_value), 'message': message_for(topic, workspace, mode, needs_text), 'status': status if status in {'accepted', 'helpful'} else 'new', 'previous_status': status, 'kind': 'prepare_workspace', 'assistance_mode': mode, 'urgency': urgency_value, 'cooldown_minutes': cooldown_minutes, 'updated_at': datetime.now(timezone.utc).isoformat()})
        suggestions.sort(key=lambda item: (item.get('priority_score', 0), item.get('confidence', 0)), reverse=True)
        visible_count = 0
        for item in suggestions:
            visible, reason = should_surface(item, allow_visible, active_workspace_exists, visible_count, max_visible)
            item['user_visible'] = visible
            item['suppressed_reason'] = reason
            if visible:
                visible_count += 1
        payload = {'suggestions': suggestions, 'updated_at': datetime.now(timezone.utc).isoformat(), 'policy': {'allow_visible': allow_visible, 'max_visible': max_visible, 'has_active_workspace': active_workspace_exists, 'visible_count': visible_count}}
        self._save(payload)
        return payload

    def set_status(self, suggestion_id: str, status: str) -> dict[str, Any]:
        data = self.snapshot()
        for suggestion in data.get('suggestions', []):
            if suggestion.get('suggestion_id') == suggestion_id:
                suggestion['status'] = status
                suggestion['previous_status'] = status
                suggestion['cooldown_minutes'] = cooldown_for_status(status)
                suggestion['updated_at'] = datetime.now(timezone.utc).isoformat()
                self._save(data)
                return suggestion
        raise KeyError(suggestion_id)
