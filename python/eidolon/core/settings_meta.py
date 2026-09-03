from __future__ import annotations

from typing import Any

from eidolon.core.settings_schema import DEFAULT_SETTINGS


def set_explicit_value(stored_values: dict[str, dict[str, Any]], area: str, key: str, value: Any) -> None:
    if area in DEFAULT_SETTINGS:
        defaults = DEFAULT_SETTINGS[area]
        if value == defaults.get(key):
            if area in stored_values:
                stored_values[area].pop(key, None)
                if not stored_values[area]:
                    stored_values.pop(area, None)
            return
        stored_values.setdefault(area, {})[key] = value
        return
    stored_values.setdefault(area, {})[key] = value


def meta_for_area(settings_store, area: str) -> dict[str, Any]:
    settings = settings_store.get_area(area)
    explicit = settings_store._stored_values.get(area, {}) if isinstance(settings_store._stored_values.get(area, {}), dict) else {}
    meta: dict[str, Any] = {}
    for key, value in settings.items():
        source = 'stored' if key in explicit or area not in DEFAULT_SETTINGS else 'default'
        meta[key] = {'source': source, 'is_default': source == 'default', 'default_value': DEFAULT_SETTINGS.get(area, {}).get(key), 'value': value}
    return meta
