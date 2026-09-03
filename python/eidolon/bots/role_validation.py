from __future__ import annotations

from typing import Any

from eidolon.bots.role_models import ALLOWED_AUTONOMY_LEVELS, REQUIRED_ROLE_FIELDS


def infer_visibility(payload: dict[str, Any]) -> str:
    return 'direct' if bool(payload.get('direct_user_counterpart')) else 'background'


def _normalize_autonomy_level(value: Any) -> str:
    result = str(value).strip()
    if result not in ALLOWED_AUTONOMY_LEVELS:
        raise ValueError(f"autonomy_level ungültig: {result}")
    return result


def _normalize_list_field(field: str, value: Any, partial: bool) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        result = [line.strip() for line in value.splitlines() if line.strip()]
    elif isinstance(value, list):
        result = [str(item).strip() for item in value if str(item).strip()]
    else:
        raise ValueError('List field must be string or list')
    if not result and not partial:
        raise ValueError(f'{field} darf nicht leer sein')
    return result


def _normalize_string_field(field: str, value: Any, partial: bool) -> str:
    result = str(value).strip()
    if not result and not partial:
        raise ValueError(f'{field} darf nicht leer sein')
    return result


def infer_role_kind(payload: dict[str, Any]) -> str:
    explicit = str(payload.get('role_kind') or '').strip()
    if explicit:
        return explicit
    role_id = str(payload.get('role_id') or '')
    KIND_BY_KEYWORD = {
        'project': 'project',
        'task': 'task',
        'meta': 'meta',
        'org': 'meta',
    }
    for keyword, kind in KIND_BY_KEYWORD.items():
        if keyword in role_id:
            return kind
    return 'operational'


def validate_payload(payload: dict[str, Any], partial: bool = False) -> dict[str, Any]:
    if not partial:
        missing = [field for field in REQUIRED_ROLE_FIELDS if field not in payload]
        if missing:
            raise ValueError(f'Fehlende Pflichtfelder: {", ".join(sorted(missing))}')
    normalized = dict(payload)
    LIST_FIELDS = ['responsibilities', 'non_responsibilities', 'activation_triggers', 'context_sources', 'success_metrics']
    for field in LIST_FIELDS:
        if field in normalized:
            normalized[field] = _normalize_list_field(field, normalized[field], partial)
    for field in ['name', 'purpose']:
        if field in normalized:
            normalized[field] = _normalize_string_field(field, normalized[field], partial)
    if 'autonomy_level' in normalized:
        normalized['autonomy_level'] = _normalize_autonomy_level(normalized['autonomy_level'])
    if 'direct_user_counterpart' in normalized:
        normalized['direct_user_counterpart'] = bool(normalized['direct_user_counterpart'])
    if 'requires_user_approval' in normalized:
        normalized['requires_user_approval'] = bool(normalized['requires_user_approval'])
    if 'description_for_user' in normalized:
        normalized['description_for_user'] = str(normalized['description_for_user']).strip()
    normalized['visibility'] = infer_visibility(normalized)
    normalized['role_kind'] = infer_role_kind(normalized)
    if 'instantiation_policy' in normalized:
        normalized['instantiation_policy'] = str(normalized['instantiation_policy']).strip() or 'explicit_approval'
    return normalized


def assert_activation_allowed(role: dict[str, Any], payload: dict[str, Any]) -> None:
    if role.get('role_id') == 'eidolon-core':
        return
    if role.get('status') != 'active':
        return
    policy = role.get('instantiation_policy') or 'explicit_approval'
    if policy == 'ephemeral_only':
        raise ValueError('ephemeral_only Rollen dürfen nicht als dauerhafte aktive Rollen gespeichert werden')
    if role.get('requires_user_approval') and payload.get('approved_by_user') is not True:
        raise ValueError('Aktivierung erfordert explizite Nutzerfreigabe via approved_by_user=true')
