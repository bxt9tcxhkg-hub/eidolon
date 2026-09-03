from __future__ import annotations

import asyncio
from typing import Any


def maybe_await(value):
    if asyncio.iscoroutine(value):
        return value
    async def _wrap():
        return value
    return _wrap()


def healthy(result: Any) -> bool:
    if isinstance(result, dict):
        if 'available' in result:
            return bool(result.get('available'))
        if 'status' in result:
            return result.get('status') not in {False, 'error', 'degraded'}
        if 'ok' in result:
            return bool(result.get('ok'))
    return bool(result)
