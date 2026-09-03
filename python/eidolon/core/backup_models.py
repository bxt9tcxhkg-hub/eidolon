from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BackupEntry:
    id: str
    timestamp: str
    reason: str
    source_dir: str
    backup_dir: str
    size_bytes: int
    file_count: int
    created_by: str
    metadata: dict[str, Any] = field(default_factory=dict)
