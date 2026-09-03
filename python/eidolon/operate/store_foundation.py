from __future__ import annotations

from pathlib import Path

from eidolon.core.config import OPERATE_DB
from eidolon.operate.store_connection import connect
from eidolon.operate.store_schema import schema_sql, migration_sql
from eidolon.operate.store_session_updates import make_id, now_iso, update_session_record


class OperateStoreFoundation:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else OPERATE_DB
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self):
        return connect(self.db_path)

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(schema_sql())
            self._run_migrations(conn)
            conn.commit()

    def _run_migrations(self, conn):
        migrations = [
            ('work_sessions', 'context_kind'),
            ('work_sessions', 'entry_message_id'),
            ('work_sessions', 'linked_workspace_id'),
            ('work_sessions', 'surface_reason'),
            ('objectives', 'candidate_source'),
            ('objectives', 'acceptance_state'),
            ('objectives', 'goal_confidence'),
            ('objectives', 'clarification_completeness'),
            ('objectives', 'linked_project_id'),
            ('agent_runs', 'product_phase'),
            ('agent_runs', 'phase_provenance'),
            ('agent_runs', 'completion_summary'),
            ('agent_runs', 'current_owner'),
            ('agent_runs', 'interrupt_classification'),
            ('evidence_items', 'evidence_severity'),
            ('evidence_items', 'is_completion_grade'),
            ('evidence_items', 'ui_digest_text'),
        ]
        for table, column in migrations:
            try:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} TEXT')
            except Exception:
                pass

    @staticmethod
    def _now() -> str:
        return now_iso()

    @staticmethod
    def _id(prefix: str) -> str:
        return make_id(prefix)

    def _update_session(self, session_id: str, **fields):
        return update_session_record(self, session_id, **fields)
