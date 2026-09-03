from __future__ import annotations


def deprecated_payload(canonical_path: str, **payload):
    return {'deprecated': True, 'canonical_path': canonical_path, **payload}


def normalize_steps(raw_steps):
    steps = raw_steps or []
    if isinstance(steps, str):
        steps = [step.strip() for step in steps.split('\n') if step.strip()]
    return steps


def active_workspace(payload: dict):
    workspaces = payload.get('workspaces', [])
    return next((workspace for workspace in workspaces if workspace.get('state') == 'active'), None)
