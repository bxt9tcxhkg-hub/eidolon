from __future__ import annotations

from eidolon.routes.api_response import api_v1_error


def require_title(request: dict) -> str:
    title = str(request.get('title') or '').strip()
    if not title:
        api_v1_error('title_required', 'Titel erforderlich')
    return title


def require_user_request(request: dict) -> str:
    user_request = str(request.get('user_request') or request.get('title') or '').strip()
    if not user_request:
        api_v1_error('user_request_required', 'user_request ist erforderlich')
    return user_request


def require_status(request: dict) -> str:
    new_status = str(request.get('status') or '').strip()
    if not new_status:
        api_v1_error('status_required', 'Status erforderlich')
    return new_status


def normalize_steps(raw_steps):
    steps = raw_steps or []
    if isinstance(steps, str):
        steps = [item.strip() for item in steps.split('\n') if item.strip()]
    return steps
