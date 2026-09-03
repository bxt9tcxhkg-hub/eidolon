from __future__ import annotations
import json
from pathlib import Path


class Persistence:
    def __init__(self, base: Path) -> None:
        self.base = base
        self.base.mkdir(parents=True, exist_ok=True)

    def load(self, name: str) -> dict:
        p = self.base / f"{name}.json"
        if not p.exists():
            return {}
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def save(self, name: str, data: dict) -> None:
        tmp = self.base / f"{name}.tmp"
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.base / f"{name}.json")
