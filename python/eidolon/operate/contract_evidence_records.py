from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from eidolon.operate.contract_types import EvidenceKind, EvidenceOwnerType, NextActionKind, TransitionActorType, TransitionType


@dataclass
class TransitionEventRecord:
    id: str
    actor_type: TransitionActorType
    actor_id: str
    transition_type: TransitionType
    from_state: str | None
    to_state: str | None
    summary: str
    evidence_ids: list[str]
    created_at: str
    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class EvidenceItemRecord:
    id: str
    owner_type: EvidenceOwnerType
    owner_id: str
    kind: EvidenceKind
    title: str
    summary: str
    artifact_ref: str | None
    metadata_json: dict[str, Any] | None
    created_at: str
    evidence_severity: Literal['info', 'warning', 'critical'] = 'info'
    is_completion_grade: bool = False
    ui_digest_text: Optional[str] = None
    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class NextActionRecord:
    kind: NextActionKind
    title: str | None
    summary: str | None
    evidence_refs: list[str]
    action_label: str | None
    action_enabled: bool
    action_reason_disabled: str | None
    execution_wired: bool = False
    def to_dict(self) -> dict[str, Any]: return asdict(self)
