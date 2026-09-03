from __future__ import annotations

import json
import sqlite3

from eidolon.operate.contracts import (
    AgentRunRecord,
    ApprovalGateRecord,
    BlockingIssueRecord,
    EvidenceItemRecord,
    ObjectiveRecord,
    SubAgentRunRecord,
    TransitionEventRecord,
    WorkSessionRecord,
)


class OperateStoreRowMappers:
    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> WorkSessionRecord:
        data = dict(row)
        data.setdefault('context_kind', 'chat_topic')
        data.setdefault('entry_message_id', None)
        data.setdefault('linked_workspace_id', None)
        data.setdefault('surface_reason', None)
        return WorkSessionRecord(**data)

    @staticmethod
    def _row_to_objective(row: sqlite3.Row) -> ObjectiveRecord:
        data = dict(row)
        data.setdefault('candidate_source', None)
        data.setdefault('acceptance_state', 'pending')
        data.setdefault('goal_confidence', 0.0)
        data.setdefault('clarification_completeness', 0.0)
        data.setdefault('linked_project_id', None)
        return ObjectiveRecord(**data)

    @staticmethod
    def _row_to_run(row: sqlite3.Row) -> AgentRunRecord:
        data = dict(row)
        data['approval_required'] = bool(data['approval_required'])
        data['interruptible'] = bool(data['interruptible'])
        data.setdefault('product_phase', None)
        data.setdefault('phase_provenance', None)
        data.setdefault('completion_summary', None)
        data.setdefault('current_owner', 'eidolon')
        data.setdefault('interrupt_classification', None)
        return AgentRunRecord(**data)

    @staticmethod
    def _row_to_subagent(row: sqlite3.Row) -> SubAgentRunRecord:
        return SubAgentRunRecord(**dict(row))

    @staticmethod
    def _row_to_blocking(row: sqlite3.Row) -> BlockingIssueRecord:
        data = dict(row)
        data['requires_user_action'] = bool(data['requires_user_action'])
        return BlockingIssueRecord(**data)

    @staticmethod
    def _row_to_approval(row: sqlite3.Row) -> ApprovalGateRecord:
        return ApprovalGateRecord(**dict(row))

    @staticmethod
    def _row_to_transition(row: sqlite3.Row) -> TransitionEventRecord:
        data = dict(row)
        data['evidence_ids'] = json.loads(data['evidence_ids'] or '[]')
        return TransitionEventRecord(**data)

    @staticmethod
    def _row_to_evidence(row: sqlite3.Row) -> EvidenceItemRecord:
        data = dict(row)
        data['metadata_json'] = json.loads(data['metadata_json']) if data.get('metadata_json') else None
        data.setdefault('evidence_severity', 'info')
        data.setdefault('is_completion_grade', False)
        data.setdefault('ui_digest_text', None)
        data['is_completion_grade'] = bool(data.get('is_completion_grade'))
        return EvidenceItemRecord(**data)
