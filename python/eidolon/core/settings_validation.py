from __future__ import annotations

from typing import Any

from eidolon.core.settings_schema import DEFAULT_SETTINGS
from eidolon.core.settings_validation_support import (
    clone_default_settings,
    derive_stored_values,
    validate_enum_value,
    validate_float_range,
    validate_int_range,
    validate_special_value,
)


def validate_value(area: str, key: str, value: Any, merged_area: dict[str, Any]) -> str | None:
    for validator in (validate_enum_value, validate_int_range, validate_float_range):
        error = validator(area, key, value)
        if error:
            return error
    return validate_special_value(area, key, value, merged_area)


def validated_area(settings: dict[str, dict[str, Any]], area: str, values: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    current = settings.get(area, dict(DEFAULT_SETTINGS[area]))
    merged = dict(current)
    updated: list[str] = []
    for key, value in values.items():
        if key not in DEFAULT_SETTINGS[area]:
            continue
        merged[key] = value
        updated.append(key)
    for key in updated:
        error = validate_value(area, key, merged[key], merged)
        if error:
            return None, error, updated
    return merged, None, updated


__all__ = [
    'clone_default_settings',
    'derive_stored_values',
    'validate_value',
    'validated_area',
]
