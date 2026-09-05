from __future__ import annotations

import json
from typing import Any

from eidolon.core.settings_schema import DEFAULT_SETTINGS, ENUM_RULES, FLOAT_RANGE_RULES, INT_RANGE_RULES

LIST_VALUE_RULES = {
    ('workspaces', 'seed_topics'),
    ('workspaces', 'enabled_modules'),
    ('skills', 'enabled_skills'),
    ('skills', 'disabled_skills'),
    ('proactive', 'ignored_topics'),
    ('autonomy', 'goals'),
    ('mesh', 'trusted_fingerprints'),
}


def _validate_http_url(value: Any, field: str, *, allow_empty: bool = False) -> str | None:
    if allow_empty and (value is None or value == ''):
        return None
    if not isinstance(value, str) or not value.startswith(('http://', 'https://')):
        return f'{field} muss mit http:// oder https:// beginnen'
    return None


def _validate_ollama_url(value: Any) -> str | None:
    return _validate_http_url(value, 'llm.ollama_url')


def _validate_base_url(value: Any) -> str | None:
    return _validate_http_url(value, 'llm.base_url', allow_empty=True)


def _validate_fallback_chain(value: Any) -> str | None:
    allowed = ENUM_RULES[('llm', 'provider')]
    if not isinstance(value, list) or not value:
        return 'llm.fallback_chain muss eine nicht-leere Liste sein'
    if any((not isinstance(item, str) or item not in allowed) for item in value):
        return 'llm.fallback_chain enthält unbekannte Provider'
    if len(set(value)) != len(value):
        return 'llm.fallback_chain darf keine Duplikate enthalten'
    return None


def _validate_list_field(area: str, key: str, value: Any) -> str | None:
    if (area, key) in LIST_VALUE_RULES and not isinstance(value, list):
        return f'{area}.{key} muss eine Liste sein'
    return None


def _validate_skill_priorities(value: Any) -> str | None:
    if not isinstance(value, dict):
        return 'skills.skill_priorities muss ein Objekt sein'
    return None


def _validate_debug_modes(value: Any) -> str | None:
    if not isinstance(value, dict):
        return 'privacy.debug_modes muss ein Objekt sein'
    if any(not isinstance(flag, bool) for flag in value.values()):
        return 'privacy.debug_modes darf nur boolesche Werte enthalten'
    return None


def _validate_network_ports(merged_area: dict[str, Any]) -> str | None:
    ports = [merged_area.get('http_port'), merged_area.get('quic_port'), merged_area.get('mesh_discovery_port')]
    if len(set(ports)) != len(ports):
        return 'network Ports müssen eindeutig sein'
    return None


SPECIAL_VALIDATORS = {
    ('llm', 'ollama_url'): _validate_ollama_url,
    ('llm', 'base_url'): _validate_base_url,
    ('llm', 'fallback_chain'): _validate_fallback_chain,
    ('skills', 'skill_priorities'): _validate_skill_priorities,
}

AREA_VALIDATORS = {
    'privacy': {('debug_modes',): _validate_debug_modes},
    'network': {('network_ports',): _validate_network_ports},
}


def clone_default_settings() -> dict[str, dict[str, Any]]:
    return {area: json.loads(json.dumps(values, ensure_ascii=False)) for area, values in DEFAULT_SETTINGS.items()}


def derive_stored_values(stored: dict[str, Any]) -> dict[str, dict[str, Any]]:
    explicit: dict[str, dict[str, Any]] = {}
    for area, defaults in DEFAULT_SETTINGS.items():
        raw_area = stored.get(area)
        if not isinstance(raw_area, dict):
            continue
        explicit_area = {
            key: value
            for key, value in raw_area.items()
            if key in defaults and value != defaults.get(key)
        }
        if explicit_area:
            explicit[area] = explicit_area
    for area, values in stored.items():
        if area.startswith('_') or area in DEFAULT_SETTINGS or not isinstance(values, dict):
            continue
        explicit[area] = dict(values)
    return explicit


def validate_enum_value(area: str, key: str, value: Any) -> str | None:
    enum_values = ENUM_RULES.get((area, key))
    if enum_values is not None and (not isinstance(value, str) or value not in enum_values):
        return f"Ungültiger Wert für {area}.{key}: {value!r}"
    return None


def validate_int_range(area: str, key: str, value: Any) -> str | None:
    int_range = INT_RANGE_RULES.get((area, key))
    if int_range is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        return f"{area}.{key} muss eine Ganzzahl sein"
    low, high = int_range
    if value < low or value > high:
        return f"{area}.{key} muss zwischen {low} und {high} liegen"
    return None


def validate_float_range(area: str, key: str, value: Any) -> str | None:
    float_range = FLOAT_RANGE_RULES.get((area, key))
    if float_range is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return f"{area}.{key} muss numerisch sein"
    low, high = float_range
    numeric = float(value)
    if numeric < low or numeric > high:
        return f"{area}.{key} muss zwischen {low} und {high} liegen"
    return None


def validate_special_value(area: str, key: str, value: Any, merged_area: dict[str, Any]) -> str | None:
    validator = SPECIAL_VALIDATORS.get((area, key))
    if validator is not None:
        return validator(value)
    validator = _validate_list_field(area, key, value)
    if validator is not None:
        return validator
    area_specific = AREA_VALIDATORS.get(area)
    if area_specific is not None:
        if key in area_specific:
            return area_specific[key](value)
    if area == 'network' and key in ('http_port', 'quic_port', 'mesh_discovery_port'):
        return _validate_network_ports(merged_area)
    return None
