from __future__ import annotations

import json
import time
from typing import Any


def message_string(payload: dict[str, Any]) -> str:
    return payload.get('text', json.dumps(payload))


def message_id(peer_id: str, started_at: float) -> str:
    return f'{peer_id}_{int(started_at * 1000)}'


def metric_payload(latency_samples: list[float], peer_ids: set[str], message_count: int, started_at: float) -> dict[str, Any]:
    runtime = max(time.time() - started_at, 0.001)
    return {
        'avg_latency': sum(latency_samples) / len(latency_samples) if latency_samples else 0,
        'peer_count': len(peer_ids),
        'msg_rate_per_sec': message_count / runtime,
        'total_messages': message_count,
        'uptime_seconds': round(runtime, 2),
    }
