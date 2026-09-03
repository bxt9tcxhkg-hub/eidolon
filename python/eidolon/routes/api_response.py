from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException


def api_v1_ok(data: dict[str, Any] | None):
    return {
        'ok': True,
        'data': data,
        'error': None,
        'serverTime': datetime.now(timezone.utc).isoformat(),
    }



def api_v1_error(code: str, message: str, status_code: int = 400):
    raise HTTPException(
        status_code=status_code,
        detail={
            'ok': False,
            'data': None,
            'error': {'code': code, 'message': message},
            'serverTime': datetime.now(timezone.utc).isoformat(),
        },
    )
