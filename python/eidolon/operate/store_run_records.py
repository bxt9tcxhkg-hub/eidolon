from __future__ import annotations

from typing import Any

from eidolon.operate.contracts import AgentRunRecord, SubAgentRunRecord


class OperateStoreRunRecordsMixin:
    def create_agent_run(self, session_id: str, objective_id: str, state: str, state_reason: str, current_phase: str, next_transition: str | None, autonomy_mode: str, approval_required: bool = False, blocking_issue_id: str | None = None, interruptible: bool = True, pending_interrupt_count: int = 0, last_interrupt_at: str | None = None, result_status: str | None = None, started_at: str | None = None, ended_at: str | None = None, product_phase: str | None = None, phase_provenance: str | None = None, completion_summary: str | None = None, current_owner: str = 'eidolon', interrupt_classification: str | None = None) -> AgentRunRecord:
        now = self._now()
        record = AgentRunRecord(id=self._id('run'), session_id=session_id, objective_id=objective_id, state=state, state_reason=state_reason, current_phase=current_phase, next_transition=next_transition, autonomy_mode=autonomy_mode, approval_required=approval_required, blocking_issue_id=blocking_issue_id, interruptible=interruptible, pending_interrupt_count=pending_interrupt_count, last_interrupt_at=last_interrupt_at, result_status=result_status, product_phase=product_phase, phase_provenance=phase_provenance, completion_summary=completion_summary, current_owner=current_owner, interrupt_classification=interrupt_classification, started_at=started_at or now, updated_at=now, ended_at=ended_at)
        with self._connect() as conn:
            conn.execute('INSERT INTO agent_runs (id, session_id, objective_id, state, state_reason, current_phase, next_transition, autonomy_mode, approval_required, blocking_issue_id, interruptible, pending_interrupt_count, last_interrupt_at, result_status, product_phase, phase_provenance, completion_summary, current_owner, interrupt_classification, started_at, updated_at, ended_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (record.id, record.session_id, record.objective_id, record.state, record.state_reason, record.current_phase, record.next_transition, record.autonomy_mode, int(record.approval_required), record.blocking_issue_id, int(record.interruptible), record.pending_interrupt_count, record.last_interrupt_at, record.result_status, record.product_phase, record.phase_provenance, record.completion_summary, record.current_owner, record.interrupt_classification, record.started_at, record.updated_at, record.ended_at))
            conn.execute('UPDATE work_sessions SET current_run_id = ?, updated_at = ? WHERE id = ?', (record.id, now, session_id))
            conn.commit()
        return record

    def get_run(self, run_id: str) -> AgentRunRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM agent_runs WHERE id = ?', (run_id,)).fetchone()
        return self._row_to_run(row) if row else None

    def get_current_run(self, session_id: str) -> AgentRunRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM agent_runs WHERE session_id = ? ORDER BY updated_at DESC LIMIT 1', (session_id,)).fetchone()
        return self._row_to_run(row) if row else None

    def update_agent_run(self, run_id: str, **fields: Any) -> AgentRunRecord:
        if not fields:
            current = self.get_run(run_id)
            if current is None:
                raise KeyError(run_id)
            return current
        fields['updated_at'] = self._now()
        assignments = ', '.join(f'{key} = ?' for key in fields)
        values = [int(value) if isinstance(value, bool) else value for value in fields.values()] + [run_id]
        with self._connect() as conn:
            cur = conn.execute(f'UPDATE agent_runs SET {assignments} WHERE id = ?', values)
            if cur.rowcount == 0:
                raise KeyError(run_id)
            conn.commit()
            row = conn.execute('SELECT * FROM agent_runs WHERE id = ?', (run_id,)).fetchone()
        return self._row_to_run(row)

    def create_subagent_run(self, parent_run_id: str, objective_id: str, display_name: str, function_type: str, mission: str, state: str, state_reason: str, assigned_by: str, blocking_issue_id: str | None = None, evidence_count: int = 0, output_count: int = 0, result_status: str | None = None, started_at: str | None = None, ended_at: str | None = None) -> SubAgentRunRecord:
        now = self._now()
        record = SubAgentRunRecord(id=self._id('sa'), parent_run_id=parent_run_id, objective_id=objective_id, display_name=display_name, function_type=function_type, mission=mission, state=state, state_reason=state_reason, assigned_by=assigned_by, blocking_issue_id=blocking_issue_id, evidence_count=evidence_count, output_count=output_count, result_status=result_status, started_at=started_at, updated_at=now, ended_at=ended_at)
        with self._connect() as conn:
            conn.execute('INSERT INTO subagent_runs (id, parent_run_id, objective_id, display_name, function_type, mission, state, state_reason, assigned_by, blocking_issue_id, evidence_count, output_count, result_status, started_at, updated_at, ended_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (record.id, record.parent_run_id, record.objective_id, record.display_name, record.function_type, record.mission, record.state, record.state_reason, record.assigned_by, record.blocking_issue_id, record.evidence_count, record.output_count, record.result_status, record.started_at, record.updated_at, record.ended_at))
            conn.commit()
        return record

    def get_subagent_run(self, subagent_id: str) -> SubAgentRunRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM subagent_runs WHERE id = ?', (subagent_id,)).fetchone()
        return self._row_to_subagent(row) if row else None

    def update_subagent_run(self, subagent_id: str, **fields: Any) -> SubAgentRunRecord:
        if not fields:
            current = self.get_subagent_run(subagent_id)
            if current is None:
                raise KeyError(subagent_id)
            return current
        fields['updated_at'] = self._now()
        assignments = ', '.join(f'{key} = ?' for key in fields)
        values = list(fields.values()) + [subagent_id]
        with self._connect() as conn:
            cur = conn.execute(f'UPDATE subagent_runs SET {assignments} WHERE id = ?', values)
            if cur.rowcount == 0:
                raise KeyError(subagent_id)
            conn.commit()
            row = conn.execute('SELECT * FROM subagent_runs WHERE id = ?', (subagent_id,)).fetchone()
        return self._row_to_subagent(row)

    def list_subagent_runs(self, run_id: str) -> list[SubAgentRunRecord]:
        with self._connect() as conn:
            rows = conn.execute('SELECT * FROM subagent_runs WHERE parent_run_id = ? ORDER BY updated_at ASC', (run_id,)).fetchall()
        return [self._row_to_subagent(row) for row in rows]
