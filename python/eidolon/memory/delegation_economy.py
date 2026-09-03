from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from eidolon.core.config import state_path


class DelegationEconomyStore:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('autonomy', 'delegation_economy.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {'scope_capability_stats': {}}
        try:
            return json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            return {'scope_capability_stats': {}}

    def _save(self, data: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def record_outcome(self, *, scope: str, capability: str, success: bool, duration: float) -> None:
        scope = 'remote' if str(scope) == 'remote' else 'local'
        capability = str(capability or 'unknown')
        data = self._load()
        stats = data.setdefault('scope_capability_stats', {})
        key = f'{scope}::{capability}'
        entry = stats.setdefault(key, {
            'scope': scope,
            'capability': capability,
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0,
            'success_rate': 0.0,
        })
        entry['attempts'] += 1
        if success:
            entry['successes'] += 1
        else:
            entry['failures'] += 1
        entry['total_duration'] = round(float(entry.get('total_duration', 0.0)) + float(duration or 0.0), 3)
        entry['avg_duration'] = round(entry['total_duration'] / entry['attempts'], 3)
        entry['success_rate'] = round(entry['successes'] / entry['attempts'], 3)
        self._save(data)

    def _aggregate_scope(self, scope: str) -> dict[str, float]:
        data = self._load()
        entries = [v for v in (data.get('scope_capability_stats') or {}).values() if v.get('scope') == scope]
        if not entries:
            return {'success_rate': 0.0, 'avg_duration': 0.0, 'attempts': 0.0}
        attempts = sum(float(e.get('attempts', 0)) for e in entries)
        successes = sum(float(e.get('successes', 0)) for e in entries)
        total_duration = sum(float(e.get('total_duration', 0.0)) for e in entries)
        return {
            'success_rate': round((successes / attempts) if attempts else 0.0, 3),
            'avg_duration': round((total_duration / attempts) if attempts else 0.0, 3),
            'attempts': attempts,
        }

    def summary(self) -> dict[str, Any]:
        local = self._aggregate_scope('local')
        remote = self._aggregate_scope('remote')
        local_score = (local['success_rate'] * 100.0) - (local['avg_duration'] * 2.0) + 6.0
        remote_score = (remote['success_rate'] * 100.0) - (remote['avg_duration'] * 2.0)
        preferred_scope = 'local' if local_score >= remote_score else 'remote'
        best = local if preferred_scope == 'local' else remote
        expected_confidence = float(best.get('success_rate', 0.0))
        expected_cost = round(float(best.get('avg_duration', 0.0)) / 10.0, 3)
        delegation_risk = round(max(0.0, 1.0 - expected_confidence) * 12.0, 3)
        return {
            'local_success_rate': local['success_rate'],
            'remote_success_rate': remote['success_rate'],
            'local_avg_duration': local['avg_duration'],
            'remote_avg_duration': remote['avg_duration'],
            'preferred_scope': preferred_scope,
            'expected_confidence': round(expected_confidence, 3),
            'expected_cost': expected_cost,
            'delegation_risk': delegation_risk,
        }

    def snapshot(self) -> dict[str, Any]:
        data = self._load()
        data['summary'] = self.summary()
        return data
