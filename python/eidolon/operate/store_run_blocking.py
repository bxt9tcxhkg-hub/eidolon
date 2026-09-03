from __future__ import annotations

from typing import Any

from eidolon.operate.contracts import ApprovalGateRecord, BlockingIssueRecord


class OperateStoreBlockingApprovalMixin:
    def create_blocking_issue(self, owner_type: str, owner_id: str, category: str, title: str, summary: str, requires_user_action: bool, resolution_hint: str | None, status: str = 'open') -> BlockingIssueRecord:
        now = self._now()
        record = BlockingIssueRecord(id=self._id('blk'), owner_type=owner_type, owner_id=owner_id, category=category, title=title, summary=summary, requires_user_action=requires_user_action, resolution_hint=resolution_hint, status=status, created_at=now, updated_at=now)
        with self._connect() as conn:
            conn.execute('INSERT INTO blocking_issues (id, owner_type, owner_id, category, title, summary, requires_user_action, resolution_hint, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (record.id, record.owner_type, record.owner_id, record.category, record.title, record.summary, int(record.requires_user_action), record.resolution_hint, record.status, record.created_at, record.updated_at))
            conn.commit()
        return record

    def get_blocking_issue(self, issue_id: str) -> BlockingIssueRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM blocking_issues WHERE id = ?', (issue_id,)).fetchone()
        return self._row_to_blocking(row) if row else None

    def update_blocking_issue(self, issue_id: str, **fields: Any) -> BlockingIssueRecord:
        if not fields:
            current = self.get_blocking_issue(issue_id)
            if current is None:
                raise KeyError(issue_id)
            return current
        fields['updated_at'] = self._now()
        assignments = ', '.join(f'{key} = ?' for key in fields)
        values = [int(value) if isinstance(value, bool) else value for value in fields.values()] + [issue_id]
        with self._connect() as conn:
            cur = conn.execute(f'UPDATE blocking_issues SET {assignments} WHERE id = ?', values)
            if cur.rowcount == 0:
                raise KeyError(issue_id)
            conn.commit()
            row = conn.execute('SELECT * FROM blocking_issues WHERE id = ?', (issue_id,)).fetchone()
        return self._row_to_blocking(row)

    def list_blocking_issues(self, owner_id: str) -> list[BlockingIssueRecord]:
        with self._connect() as conn:
            rows = conn.execute('SELECT * FROM blocking_issues WHERE owner_id = ? ORDER BY created_at ASC', (owner_id,)).fetchall()
        return [self._row_to_blocking(row) for row in rows]

    def create_approval_gate(self, run_id: str, title: str, summary: str, action_type: str, status: str = 'pending', requested_at: str | None = None, resolved_at: str | None = None, resolved_by: str | None = None) -> ApprovalGateRecord:
        record = ApprovalGateRecord(id=self._id('apr'), run_id=run_id, title=title, summary=summary, action_type=action_type, status=status, requested_at=requested_at or self._now(), resolved_at=resolved_at, resolved_by=resolved_by)
        with self._connect() as conn:
            conn.execute('INSERT INTO approval_gates (id, run_id, title, summary, action_type, status, requested_at, resolved_at, resolved_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (record.id, record.run_id, record.title, record.summary, record.action_type, record.status, record.requested_at, record.resolved_at, record.resolved_by))
            conn.commit()
        return record

    def get_approval_gate(self, gate_id: str) -> ApprovalGateRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM approval_gates WHERE id = ?', (gate_id,)).fetchone()
        return self._row_to_approval(row) if row else None

    def update_approval_gate(self, gate_id: str, **fields: Any) -> ApprovalGateRecord:
        if not fields:
            current = self.get_approval_gate(gate_id)
            if current is None:
                raise KeyError(gate_id)
            return current
        assignments = ', '.join(f'{key} = ?' for key in fields)
        values = list(fields.values()) + [gate_id]
        with self._connect() as conn:
            cur = conn.execute(f'UPDATE approval_gates SET {assignments} WHERE id = ?', values)
            if cur.rowcount == 0:
                raise KeyError(gate_id)
            conn.commit()
            row = conn.execute('SELECT * FROM approval_gates WHERE id = ?', (gate_id,)).fetchone()
        return self._row_to_approval(row)

    def list_approval_gates(self, run_id: str) -> list[ApprovalGateRecord]:
        with self._connect() as conn:
            rows = conn.execute('SELECT * FROM approval_gates WHERE run_id = ? ORDER BY requested_at ASC', (run_id,)).fetchall()
        return [self._row_to_approval(row) for row in rows]
