"""Zentraler Settings-Store für Eidolon — persistiert alle Benutzereinstellungen."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.core.settings_meta import meta_for_area, set_explicit_value
from eidolon.core.settings_mutations import set_area as apply_set_area, set_value as apply_set, update_area as apply_update_area
from eidolon.core.settings_persistence import load_settings, save_settings
from eidolon.core.settings_store_helpers import (
    bool_property,
    default_settings_store_root,
    get_all_with_meta_payload,
    get_area,
    get_area_with_meta,
    get_value,
    int_property,
    reset_all,
    reset_area,
    settings_snapshot,
    str_property,
)


class SettingsStore:
    """Zentraler Store für alle Benutzereinstellungen mit sofortiger Persistenz."""

    def __init__(self, project_root: Path):
        from eidolon.core.config import state_path
        self._path = state_path('user', 'settings.json', project_root=project_root)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._settings: dict[str, dict[str, Any]] = {}
        self._stored_values: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        self._settings, self._stored_values = load_settings(self._path)

    def _save(self) -> None:
        save_settings(self._path, self._stored_values)

    def _set_explicit_value(self, area: str, key: str, value: Any) -> None:
        set_explicit_value(self._stored_values, area, key, value)

    def _meta_for_area(self, area: str) -> dict[str, Any]:
        return meta_for_area(self, area)

    get_all = settings_snapshot
    get_all_with_meta = get_all_with_meta_payload
    get_area = get_area
    get_area_with_meta = get_area_with_meta
    get = get_value
    reset_area = reset_area
    reset_all = reset_all

    def update_area(self, area: str, values: dict[str, Any]) -> dict[str, Any]:
        return apply_update_area(self, area, values)

    def set(self, area: str, key: str, value: Any) -> dict[str, Any]:
        return apply_set(self, area, key, value)

    def set_area(self, area: str, values: dict[str, Any]) -> dict[str, Any]:
        return apply_set_area(self, area, values)

    http_port = int_property('network', 'http_port', 8002)
    quic_port = int_property('network', 'quic_port', 4434)
    llm_model = str_property('llm', 'model', 'llama3.1:8b')
    llm_provider = str_property('llm', 'provider', 'ollama')
    autonomy_level = str_property('autonomy', 'level', 'proactive')
    proactive_enabled = bool_property('proactive', 'enabled', True)
    theme = str_property('ui', 'theme', 'dark')
    language = str_property('ui', 'language', 'de')


_store: SettingsStore | None = None


def get_settings_store() -> SettingsStore:
    global _store
    if _store is None:
        _store = SettingsStore(default_settings_store_root())
    return _store


def init_settings_store(project_root: Path) -> SettingsStore:
    global _store
    _store = SettingsStore(project_root)
    return _store
