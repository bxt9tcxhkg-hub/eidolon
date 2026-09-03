from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_log(log_path: Path, entry: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    data = []
    if log_path.exists():
        try:
            data = json.loads(log_path.read_text(encoding='utf-8'))
        except Exception:
            data = []
    data.append(entry)
    log_path.write_text(json.dumps(data[-200:], ensure_ascii=False, indent=2), encoding='utf-8')
