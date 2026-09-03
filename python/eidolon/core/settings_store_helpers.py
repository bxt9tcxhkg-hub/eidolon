from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.core.settings_meta import meta_for_area
from eidolon.core.settings_schema import DEFAULT_SETTINGS


def default_settings_store_root() -> Path:
    return Path(__file__).resolve().parents[2].parent


def settings_snapshot(settings_store) -> dict[str, dict[str, Any]]:
    return {area: dict(values) for area, values in settings_store._settings.items()}


def get_all_with_meta_payload(settings_store) -> dict[str, Any]:
    settings = settings_snapshot(settings_store)
    meta = {area: meta_for_area(settings_store, area) for area in settings.keys()}
    return {
        'settings': settings,
        'meta': meta,
        'source_counts': {
            'default': sum(1 for area in meta.values() for item in area.values() if item.get('source') == 'default'),
            'stored': sum(1 for area in meta.values() for item in area.values() if item.get('source') == 'stored'),
        },
    }


def get_area(settings_store, area: str) -> dict[str, Any]:
    return dict(settings_store._settings[area]) if area in settings_store._settings else dict(DEFAULT_SETTINGS.get(area, {}))


def get_area_with_meta(settings_store, area: str) -> dict[str, Any]:
    return {'settings': get_area(settings_store, area), 'meta': meta_for_area(settings_store, area)}


def get_value(settings_store, area: str, key: str, default: Any = None) -> Any:
    if key in settings_store._settings.get(area, {}):
        return settings_store._settings[area][key]
    return DEFAULT_SETTINGS.get(area, {}).get(key, default)


def reset_area(settings_store, area: str) -> dict[str, Any]:
    if area not in DEFAULT_SETTINGS:
        return {'ok': False, 'error': f'Unbekannter Bereich: {area}'}
    settings_store._settings[area] = dict(DEFAULT_SETTINGS[area])
    settings_store._stored_values.pop(area, None)
    settings_store._save()
    return {'ok': True, 'area': area, 'note': 'Auf Defaults zurückgesetzt'}


def reset_all(settings_store) -> dict[str, Any]:
    settings_store._settings = {area: dict(values) for area, values in DEFAULT_SETTINGS.items()}
    settings_store._stored_values = {}
    settings_store._save()
    return {'ok': True, 'note': 'Alle Einstellungen auf Defaults zurückgesetzt'}


def int_property(area: str, key: str, default: int):
    return property(lambda self: int(get_value(self, area, key, default)))


def str_property(area: str, key: str, default: str):
    return property(lambda self: str(get_value(self, area, key, default)))


def bool_property(area: str, key: str, default: bool):
    return property(lambda self: bool(get_value(self, area, key, default)))
