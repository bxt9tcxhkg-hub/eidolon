from __future__ import annotations

import json
from datetime import datetime, timezone

from eidolon.bots.role_catalog import default_roles
from eidolon.bots.role_models import BotRole


def load_registry(path) -> dict:
    if not path.exists():
        return {'roles': [], 'updated_at': None}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {'roles': [], 'updated_at': None}


def save_registry(path, data: dict) -> None:
    data['updated_at'] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def ensure_default_templates(path, data: dict) -> dict:
    default_map = {role.role_id: role.to_dict() for role in default_roles()}
    roles = []
    existing_ids = set()
    changed = False
    for raw in data.get('roles', []):
        role = BotRole.from_dict(raw).to_dict()
        role_id = role.get('role_id')
        existing_ids.add(role_id)
        default = default_map.get(role_id)
        if default:
            merged = {**default, **role}
            if merged.get('direct_user_counterpart'):
                merged['visibility'] = 'direct'
            if role_id == 'eidolon-core':
                merged['instantiation_policy'] = 'always_on'
            if merged != role:
                changed = True
            role = merged
        roles.append(role)
    for role in default_roles():
        if role.role_id in existing_ids:
            continue
        roles.append(role.to_dict())
        changed = True
    if changed:
        data['roles'] = roles
        save_registry(path, data)
    return data


def bootstrap_defaults(path) -> None:
    data = load_registry(path)
    if data.get('roles'):
        return
    data['roles'] = [role.to_dict() for role in default_roles()]
    save_registry(path, data)
