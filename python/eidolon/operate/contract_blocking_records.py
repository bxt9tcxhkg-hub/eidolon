from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal

from eidolon.operate.contract_types import ApprovalActionType, BlockingCategory, BlockingOwnerType


@dataclass
class BlockingIssueRecord:
    id: str
    owner_type: BlockingOwnerType
    owner_id: str
    category: BlockingCategory
    title: str
    summary: str
    requires_user_action: bool
    resolution_hint: str | None
    status: Literal['open', 'resolved', 'superseded']
    created_at: str
    updated_at: str
    def to_dict(self) -> dict[str, Any]: return asdict(self)


@dataclass
class ApprovalGateRecord:
    id: str
    run_id: str
    title: str
    summary: str
    action_type: ApprovalActionType
    status: Literal['pending', 'approved', 'rejected', 'expired']
    requested_at: str
    resolved_at: str | None
    resolved_by: Literal['user', 'system'] | None
    def to_dict(self) -> dict[str, Any]: return asdict(self)
