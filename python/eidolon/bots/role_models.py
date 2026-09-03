from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

REQUIRED_ROLE_FIELDS = {
    'name',
    'purpose',
    'responsibilities',
    'non_responsibilities',
    'activation_triggers',
    'autonomy_level',
    'direct_user_counterpart',
    'requires_user_approval',
    'context_sources',
    'success_metrics',
}

ALLOWED_AUTONOMY_LEVELS = {
    'advisory_only',
    'execution_within_guardrails',
    'background_analysis',
}


@dataclass
class BotRole:
    role_id: str
    name: str
    purpose: str
    responsibilities: list[str]
    non_responsibilities: list[str]
    activation_triggers: list[str]
    autonomy_level: str
    direct_user_counterpart: bool
    requires_user_approval: bool
    context_sources: list[str]
    success_metrics: list[str]
    parent_role_id: str | None = None
    visibility: str = 'background'
    status: str = 'active'
    role_kind: str = 'operational'
    instantiation_policy: str = 'explicit_approval'
    description_for_user: str = ''
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'BotRole':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
