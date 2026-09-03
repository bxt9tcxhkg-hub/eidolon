from __future__ import annotations

from typing import Any

from eidolon.core.settings_schema import DEFAULT_SETTINGS
from eidolon.core.settings_validation import validated_area


def update_area(settings_store, area: str, values: dict[str, Any]) -> dict[str, Any]:
    if area not in DEFAULT_SETTINGS:
        return {'ok': False, 'error': f'Unbekannter Bereich: {area}'}
    current, error, updated = validated_area(settings_store._settings, area, values)
    if error:
        return {'ok': False, 'error': error}
    for key in updated:
        settings_store._set_explicit_value(area, key, current[key])
    settings_store._settings[area] = current
    settings_store._save()
    return {'ok': True, 'area': area, 'updated': updated}


def set_value(settings_store, area: str, key: str, value: Any) -> dict[str, Any]:
    if area not in DEFAULT_SETTINGS:
        return {'ok': False, 'error': f'Unbekannter Bereich: {area}'}
    if key not in DEFAULT_SETTINGS[area]:
        return {'ok': False, 'error': f'Unbekannter Schlüssel: {key}'}
    current, error, _updated = validated_area(settings_store._settings, area, {key: value})
    if error:
        return {'ok': False, 'error': error}
    settings_store._settings[area] = current
    settings_store._set_explicit_value(area, key, value)
    settings_store._save()
    return {'ok': True, 'area': area, 'key': key, 'value': value}


def set_area(settings_store, area: str, values: dict[str, Any]) -> dict[str, Any]:
    if area not in DEFAULT_SETTINGS:
        current = {**settings_store._settings.get(area, {}), **values}
        settings_store._settings[area] = current
        settings_store._stored_values[area] = dict(current)
        settings_store._save()
        return {'ok': True, 'area': area, 'updated': list(values.keys())}
    current, error, updated = validated_area(settings_store._settings, area, values)
    if error:
        return {'ok': False, 'error': error}
    for key in updated:
        settings_store._set_explicit_value(area, key, current[key])
    settings_store._settings[area] = current
    settings_store._save()
    return {'ok': True, 'area': area, 'updated': updated}
