from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Device:
    id: str
    name: str
    device_type: str = "unknown"
    platform: str = "unknown"
    last_seen: str | None = None
    status: str = "offline"
    capabilities: list[str] = field(default_factory=list)
    connection: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldStore:
    devices: dict[str, Device] = field(default_factory=dict)

    def snapshot(self) -> list[dict[str, Any]]:
        return [d.__dict__ for d in self.devices.values()]
