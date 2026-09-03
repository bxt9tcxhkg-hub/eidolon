from __future__ import annotations

from eidolon.operate.contracts import ObjectiveRecord, WorkSessionRecord


class OperateStoreSessionObjectiveMixin:
    def create_session(self, title: str, source_kind: str, current_view: str, status: str = 'active', context_kind: str = 'chat_topic', entry_message_id: str | None = None, linked_workspace_id: str | None = None, surface_reason: str | None = None) -> WorkSessionRecord:
        now = self._now()
        record = WorkSessionRecord(
            id=self._id('ws'),
            title=title,
            status=status,
            current_run_id=None,
            current_objective_id=None,
            current_view=current_view,
            source_kind=source_kind,
            context_kind=context_kind,
            entry_message_id=entry_message_id,
            linked_workspace_id=linked_workspace_id,
            surface_reason=surface_reason,
            created_at=now,
            updated_at=now,
        )
        with self._connect() as conn:
            conn.execute(
                'INSERT INTO work_sessions (id, title, status, current_run_id, current_objective_id, current_view, source_kind, context_kind, entry_message_id, linked_workspace_id, surface_reason, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (record.id, record.title, record.status, record.current_run_id, record.current_objective_id, record.current_view, record.source_kind, record.context_kind, record.entry_message_id, record.linked_workspace_id, record.surface_reason, record.created_at, record.updated_at),
            )
            conn.commit()
        return record

    def get_session(self, session_id: str) -> WorkSessionRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM work_sessions WHERE id = ?', (session_id,)).fetchone()
        return self._row_to_session(row) if row else None

    def get_current_session(self) -> WorkSessionRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM work_sessions ORDER BY updated_at DESC LIMIT 1').fetchone()
        return self._row_to_session(row) if row else None

    def update_session(self, session_id: str, **fields: Any) -> WorkSessionRecord:
        return self._update_session(session_id, **fields)

    def create_objective(self, session_id: str, title: str, user_request: str, normalized_goal: str, scope_summary: str, decomposition_mode: str, status: str = 'active', candidate_source: str | None = None, acceptance_state: str = 'pending', goal_confidence: float = 0.0, clarification_completeness: float = 0.0, linked_project_id: str | None = None) -> ObjectiveRecord:
        now = self._now()
        record = ObjectiveRecord(
            id=self._id('obj'),
            session_id=session_id,
            title=title,
            user_request=user_request,
            normalized_goal=normalized_goal,
            scope_summary=scope_summary,
            decomposition_mode=decomposition_mode,
            status=status,
            candidate_source=candidate_source,
            acceptance_state=acceptance_state,
            goal_confidence=goal_confidence,
            clarification_completeness=clarification_completeness,
            linked_project_id=linked_project_id,
            created_at=now,
            updated_at=now,
        )
        with self._connect() as conn:
            conn.execute(
                'INSERT INTO objectives (id, session_id, title, user_request, normalized_goal, scope_summary, decomposition_mode, status, candidate_source, acceptance_state, goal_confidence, clarification_completeness, linked_project_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (record.id, record.session_id, record.title, record.user_request, record.normalized_goal, record.scope_summary, record.decomposition_mode, record.status, record.candidate_source, record.acceptance_state, record.goal_confidence, record.clarification_completeness, record.linked_project_id, record.created_at, record.updated_at),
            )
            conn.execute(
                'UPDATE work_sessions SET current_objective_id = ?, updated_at = ? WHERE id = ?',
                (record.id, now, session_id),
            )
            conn.commit()
        return record

    def get_objective(self, objective_id: str) -> ObjectiveRecord | None:
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM objectives WHERE id = ?', (objective_id,)).fetchone()
        return self._row_to_objective(row) if row else None

    def update_objective(self, objective_id: str, **fields: Any) -> ObjectiveRecord:
        if not fields:
            current = self.get_objective(objective_id)
            if current is None:
                raise KeyError(objective_id)
            return current
        fields['updated_at'] = self._now()
        assignments = ', '.join(f'{key} = ?' for key in fields)
        values = list(fields.values()) + [objective_id]
        with self._connect() as conn:
            cur = conn.execute(f'UPDATE objectives SET {assignments} WHERE id = ?', values)
            if cur.rowcount == 0:
                raise KeyError(objective_id)
            conn.commit()
            row = conn.execute('SELECT * FROM objectives WHERE id = ?', (objective_id,)).fetchone()
        return self._row_to_objective(row)
