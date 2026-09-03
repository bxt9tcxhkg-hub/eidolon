from __future__ import annotations

SCHEMA_STATEMENTS = [
    '''
    CREATE TABLE IF NOT EXISTS work_sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        current_run_id TEXT,
        current_objective_id TEXT,
        current_view TEXT NOT NULL,
        source_kind TEXT NOT NULL,
        context_kind TEXT NOT NULL DEFAULT 'chat_topic',
        entry_message_id TEXT,
        linked_workspace_id TEXT,
        surface_reason TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS objectives (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        title TEXT NOT NULL,
        user_request TEXT NOT NULL,
        normalized_goal TEXT NOT NULL,
        scope_summary TEXT NOT NULL,
        decomposition_mode TEXT NOT NULL,
        status TEXT NOT NULL,
        candidate_source TEXT,
        acceptance_state TEXT NOT NULL DEFAULT 'pending',
        goal_confidence REAL NOT NULL DEFAULT 0.0,
        clarification_completeness REAL NOT NULL DEFAULT 0.0,
        linked_project_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS agent_runs (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        objective_id TEXT NOT NULL,
        state TEXT NOT NULL,
        state_reason TEXT NOT NULL,
        current_phase TEXT NOT NULL,
        next_transition TEXT,
        autonomy_mode TEXT NOT NULL,
        approval_required INTEGER NOT NULL,
        blocking_issue_id TEXT,
        interruptible INTEGER NOT NULL,
        pending_interrupt_count INTEGER NOT NULL,
        last_interrupt_at TEXT,
        result_status TEXT,
        product_phase TEXT,
        phase_provenance TEXT,
        completion_summary TEXT,
        current_owner TEXT NOT NULL DEFAULT 'eidolon',
        interrupt_classification TEXT,
        started_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        ended_at TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS subagent_runs (
        id TEXT PRIMARY KEY,
        parent_run_id TEXT NOT NULL,
        objective_id TEXT NOT NULL,
        display_name TEXT NOT NULL,
        function_type TEXT NOT NULL,
        mission TEXT NOT NULL,
        state TEXT NOT NULL,
        state_reason TEXT NOT NULL,
        assigned_by TEXT NOT NULL,
        blocking_issue_id TEXT,
        evidence_count INTEGER NOT NULL,
        output_count INTEGER NOT NULL,
        result_status TEXT,
        started_at TEXT,
        updated_at TEXT NOT NULL,
        ended_at TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS blocking_issues (
        id TEXT PRIMARY KEY,
        owner_type TEXT NOT NULL,
        owner_id TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        requires_user_action INTEGER NOT NULL,
        resolution_hint TEXT,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS approval_gates (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        action_type TEXT NOT NULL,
        status TEXT NOT NULL,
        requested_at TEXT NOT NULL,
        resolved_at TEXT,
        resolved_by TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS transition_events (
        id TEXT PRIMARY KEY,
        actor_type TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        transition_type TEXT NOT NULL,
        from_state TEXT,
        to_state TEXT,
        summary TEXT NOT NULL,
        evidence_ids TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS evidence_items (
        id TEXT PRIMARY KEY,
        owner_type TEXT NOT NULL,
        owner_id TEXT NOT NULL,
        kind TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        artifact_ref TEXT,
        metadata_json TEXT,
        evidence_severity TEXT NOT NULL DEFAULT 'info',
        is_completion_grade INTEGER NOT NULL DEFAULT 0,
        ui_digest_text TEXT,
        created_at TEXT NOT NULL
    )
    ''',
]

ALTER_TABLE_STATEMENTS = [
    'ALTER TABLE work_sessions ADD COLUMN IF NOT EXISTS context_kind TEXT NOT NULL DEFAULT \'chat_topic\'',
    'ALTER TABLE work_sessions ADD COLUMN IF NOT EXISTS entry_message_id TEXT',
    'ALTER TABLE work_sessions ADD COLUMN IF NOT EXISTS linked_workspace_id TEXT',
    'ALTER TABLE work_sessions ADD COLUMN IF NOT EXISTS surface_reason TEXT',
    'ALTER TABLE objectives ADD COLUMN IF NOT EXISTS candidate_source TEXT',
    'ALTER TABLE objectives ADD COLUMN IF NOT EXISTS acceptance_state TEXT NOT NULL DEFAULT \'pending\'',
    'ALTER TABLE objectives ADD COLUMN IF NOT EXISTS goal_confidence REAL NOT NULL DEFAULT 0.0',
    'ALTER TABLE objectives ADD COLUMN IF NOT EXISTS clarification_completeness REAL NOT NULL DEFAULT 0.0',
    'ALTER TABLE objectives ADD COLUMN IF NOT EXISTS linked_project_id TEXT',
    'ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS product_phase TEXT',
    'ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS phase_provenance TEXT',
    'ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS completion_summary TEXT',
    'ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS current_owner TEXT NOT NULL DEFAULT \'eidolon\'',
    'ALTER TABLE agent_runs ADD COLUMN IF NOT EXISTS interrupt_classification TEXT',
    'ALTER TABLE evidence_items ADD COLUMN IF NOT EXISTS evidence_severity TEXT NOT NULL DEFAULT \'info\'',
    'ALTER TABLE evidence_items ADD COLUMN IF NOT EXISTS is_completion_grade INTEGER NOT NULL DEFAULT 0',
    'ALTER TABLE evidence_items ADD COLUMN IF NOT EXISTS ui_digest_text TEXT',
]

def schema_sql() -> str:
    return ' ;\n'.join(statement.strip() for statement in SCHEMA_STATEMENTS) + ';\n'

def migration_sql() -> str:
    return ' ;\n'.join(statement for statement in ALTER_TABLE_STATEMENTS) + ';\n'
