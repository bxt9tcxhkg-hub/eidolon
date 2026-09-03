from __future__ import annotations

import uuid
from datetime import datetime, timezone

from eidolon.bots.role_models import BotRole
from eidolon.bots.role_validation import assert_activation_allowed, infer_visibility, validate_payload


def registry_summary(roles: list[dict]) -> dict:
    return {
        'total': len(roles),
        'active': sum(1 for role in roles if role.get('status') == 'active'),
        'defined': sum(1 for role in roles if role.get('status') == 'defined'),
        'direct_counterparts': sum(1 for role in roles if role.get('direct_user_counterpart')),
        'background_roles': sum(1 for role in roles if not role.get('direct_user_counterpart')),
        'role_kinds': sorted({str(role.get('role_kind') or 'operational') for role in roles}),
    }


def create_role(data: dict, payload: dict) -> dict:
    normalized = validate_payload(payload, partial=False)
    role = BotRole(
        role_id=normalized.get('role_id') or f"bot-{uuid.uuid4().hex[:10]}",
        name=normalized['name'], purpose=normalized['purpose'], responsibilities=normalized['responsibilities'], non_responsibilities=normalized['non_responsibilities'], activation_triggers=normalized['activation_triggers'], autonomy_level=normalized['autonomy_level'], direct_user_counterpart=normalized['direct_user_counterpart'], requires_user_approval=normalized['requires_user_approval'], context_sources=normalized['context_sources'], success_metrics=normalized['success_metrics'], parent_role_id=normalized.get('parent_role_id'), visibility=normalized.get('visibility', 'background'), status=normalized.get('status', 'defined'), role_kind=normalized.get('role_kind', 'operational'), instantiation_policy=normalized.get('instantiation_policy', 'explicit_approval'), description_for_user=normalized.get('description_for_user', ''),
    )
    assert_activation_allowed(role.to_dict(), payload)
    if any(existing.get('role_id') == role.role_id for existing in data.get('roles', [])):
        raise ValueError('role_id bereits vorhanden')
    data.setdefault('roles', []).append(role.to_dict())
    return role.to_dict()


def update_role(data: dict, role_id: str, payload: dict) -> dict:
    normalized = validate_payload(payload, partial=True)
    for idx, existing in enumerate(data.get('roles', [])):
        if existing.get('role_id') != role_id:
            continue
        updated = dict(existing)
        updated.update(normalized)
        updated['role_id'] = role_id
        updated['updated_at'] = datetime.now(timezone.utc).isoformat()
        updated['visibility'] = infer_visibility(updated)
        assert_activation_allowed(updated, payload)
        data['roles'][idx] = updated
        return updated
    raise KeyError(role_id)


def delete_role(data: dict, role_id: str) -> dict:
    if role_id == 'eidolon-core':
        raise ValueError('eidolon-core ist die direkte Hauptrolle und darf nicht gelöscht werden')
    roles = data.get('roles', [])
    for idx, existing in enumerate(roles):
        if existing.get('role_id') != role_id:
            continue
        removed = roles.pop(idx)
        data['roles'] = roles
        return removed
    raise KeyError(role_id)
