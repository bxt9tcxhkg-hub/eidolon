from __future__ import annotations

import json
from typing import Any

from eidolon.operate.contracts import EvidenceItemRecord, TransitionEventRecord


class OperateStoreEvidenceTransitionMixin:
    def create_evidence_item(self, owner_type: str, owner_id: str, kind: str, title: str, summary: str, artifact_ref: str | None, metadata_json: dict[str, Any] | None, evidence_severity: str = 'info', is_completion_grade: bool = False, ui_digest_text: str | None = None) -> EvidenceItemRecord:
        record = EvidenceItemRecord(id=self._id('ev'), owner_type=owner_type, owner_id=owner_id, kind=kind, title=title, summary=summary, artifact_ref=artifact_ref, metadata_json=metadata_json, created_at=self._now(), evidence_severity=evidence_severity, is_completion_grade=is_completion_grade, ui_digest_text=ui_digest_text)
        with self._connect() as conn:
            conn.execute('INSERT INTO evidence_items (id, owner_type, owner_id, kind, title, summary, artifact_ref, metadata_json, created_at, evidence_severity, is_completion_grade, ui_digest_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (record.id, record.owner_type, record.owner_id, record.kind, record.title, record.summary, record.artifact_ref, json.dumps(record.metadata_json, ensure_ascii=False) if record.metadata_json is not None else None, record.created_at, record.evidence_severity, int(record.is_completion_grade), record.ui_digest_text))
            if owner_type == 'subagent':
                conn.execute('UPDATE subagent_runs SET evidence_count = evidence_count + 1, updated_at = ? WHERE id = ?', (record.created_at, owner_id))
            conn.commit()
        return record

    def list_evidence_items(self, run_id: str) -> list[EvidenceItemRecord]:
        with self._connect() as conn:
            rows = conn.execute('''
                SELECT * FROM evidence_items
                WHERE (owner_type = 'run' AND owner_id = ?)
                   OR (owner_type = 'subagent' AND owner_id IN (SELECT id FROM subagent_runs WHERE parent_run_id = ?))
                   OR (owner_type = 'objective' AND owner_id IN (SELECT objective_id FROM agent_runs WHERE id = ?))
                ORDER BY created_at ASC
                ''', (run_id, run_id, run_id)).fetchall()
        return [self._row_to_evidence(row) for row in rows]

    def append_transition_event(self, actor_type: str, actor_id: str, transition_type: str, from_state: str | None, to_state: str | None, summary: str, evidence_ids: list[str]) -> TransitionEventRecord:
        record = TransitionEventRecord(id=self._id('tr'), actor_type=actor_type, actor_id=actor_id, transition_type=transition_type, from_state=from_state, to_state=to_state, summary=summary, evidence_ids=list(evidence_ids), created_at=self._now())
        with self._connect() as conn:
            conn.execute('INSERT INTO transition_events (id, actor_type, actor_id, transition_type, from_state, to_state, summary, evidence_ids, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (record.id, record.actor_type, record.actor_id, record.transition_type, record.from_state, record.to_state, record.summary, json.dumps(record.evidence_ids, ensure_ascii=False), record.created_at))
            conn.commit()
        return record

    def list_transition_events(self, run_id: str) -> list[TransitionEventRecord]:
        with self._connect() as conn:
            rows = conn.execute('''
                SELECT * FROM transition_events
                WHERE actor_id = ? OR actor_id IN (SELECT id FROM subagent_runs WHERE parent_run_id = ?)
                ORDER BY created_at ASC
                ''', (run_id, run_id)).fetchall()
        return [self._row_to_transition(row) for row in rows]
