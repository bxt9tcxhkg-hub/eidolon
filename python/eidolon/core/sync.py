from __future__ import annotations
import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SyncOp:
    op_id: str
    op_type: str
    entity: str
    key: str
    value: Any
    source_device: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class SyncState:
    def __init__(self) -> None:
        self.devices: dict[str, dict[str, Any]] = {}
        self.ops: list[SyncOp] = []

    def enqueue(self, op: SyncOp) -> None:
        self.ops.append(op)

    def pending_for(self, device_id: str) -> list[dict[str, Any]]:
        return [op.__dict__ for op in self.ops]
