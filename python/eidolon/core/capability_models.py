from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


CheckFn = Callable[[], bool]


@dataclass
class Capability:
    id: str
    description: str
    name: str | None = None
    provider: str = 'local'
    inputs: dict[str, str] = field(default_factory=dict)
    outputs: dict[str, str] = field(default_factory=dict)
    permissions: list[str] = field(default_factory=list)
    _check_fn: CheckFn = lambda: True
    detail: str = ''

    def check_available(self) -> bool:
        try:
            return bool(self._check_fn())
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        available = self.check_available()
        return {
            'id': self.id,
            'name': self.name or self.id.replace('.', '_'),
            'description': self.description,
            'provider': self.provider,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'permissions': self.permissions,
            'available': available,
            'detail': self.detail if self.detail else ('available' if available else 'unavailable'),
        }


class CapabilityRegistry:
    def __init__(self):
        self._caps: dict[str, Capability] = {}

    def register(self, cap: Capability) -> None:
        self._caps[cap.id] = cap

    def get(self, cap_id: str) -> Capability | None:
        return self._caps.get(cap_id)

    def list(self) -> list[dict[str, Any]]:
        return [self._caps[key].to_dict() for key in sorted(self._caps.keys())]

    def available(self) -> list[dict[str, Any]]:
        return [cap.to_dict() for cap in self._caps.values() if cap.check_available()]

    def unavailable(self) -> list[dict[str, Any]]:
        return [cap.to_dict() for cap in self._caps.values() if not cap.check_available()]

    def as_dict(self) -> dict[str, Capability]:
        return dict(self._caps)
