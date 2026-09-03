from __future__ import annotations

from datetime import datetime, timezone


def learned_score(orchestrator, workspace_type: str, module_id: str, action: str) -> tuple[float, float]:
    if not orchestrator.memory:
        return 0.0, 0.0
    confidence = orchestrator.memory.get_module_confidence(workspace_type, module_id, action)
    bonus = round((confidence - 0.5) * 0.7, 3)
    return confidence, bonus


def compose(orchestrator, workspace_type: str, module_id: str, action: str, label: str, base_score: float, reason: str, payload: dict) -> dict:
    confidence, bonus = learned_score(orchestrator, workspace_type, module_id, action)
    total = round(base_score + bonus, 3)
    if confidence > 0:
        reason = f"{reason} Historische Erfolgsrate für {module_id}: {confidence:.2f}."
    return {'module_id': module_id, 'action': action, 'label': label, 'priority_score': total, 'base_score': round(base_score, 3), 'learned_confidence': confidence, 'reason': reason, 'payload': payload}


def default_snapshot(workspace: dict, next_best: dict, ranked: list[dict], posture: str, memory_enabled: bool) -> dict:
    return {'updated_at': datetime.now(timezone.utc).isoformat(), 'workspace_id': workspace.get('workspace_id'), 'topic_label': workspace.get('topic_label'), 'recommended_mode': next_best['module_id'], 'next_best_action': next_best, 'ranked_modes': ranked, 'autonomy_posture': posture, 'learning_enabled': memory_enabled}
