from __future__ import annotations

import json
import urllib.request
from pathlib import Path


def api_call(port: int, method: str, path: str, body: dict | None = None) -> dict:
    url = f'http://127.0.0.1:{port}{path}'
    data = json.dumps(body or {}).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method=method)
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read().decode())


def write_status(status_path: Path, payload: dict):
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
