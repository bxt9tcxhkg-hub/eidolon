from __future__ import annotations

import re
from typing import Any

from eidolon.core.llm_provider_catalog import PRESET_IDS, PROVIDER_IDS
from eidolon.core.settings_schema import DEFAULT_SETTINGS, ENUM_RULES

_APPLY_VERBS = (
    'setze', 'setz ', 'stelle ', 'stell ', 'ändere', 'aendere', 'konfiguriere', 'konfigurier',
    'schalte', 'nimm ', 'übernimm', 'uebernimm',
)
_APPLY_PHRASES = (
    'ersatzkette auf', 'fallback-kette auf', 'fallback kette auf', 'fallback auf',
    'anbieter auf', 'provider auf', 'als anbieter', 'als provider',
    'einstellung auf', 'einstellungen auf', 'thema auf', 'theme auf',
)
_SETTINGS_NOUNS = (
    'ersatzkette', 'fallback', 'anbieter', 'provider', 'einstellung', 'preset', 'vorlage',
    'modell', 'model', 'basis-url', 'base_url', 'ollama-url', 'temperatur', 'thema', 'theme',
    'sprache', 'language', 'dichte', 'density', 'animation', 'http_port', 'quic_port',
)
_QUESTION_MARKERS = ('?', 'was wäre', 'was waere', 'sollten wir', 'würdest du empfehlen', 'wuerdest du empfehlen', 'was hältst du', 'was haeltst du')
_WORK_ONLY_PHRASES = (
    'setz das um', 'stelle das um', 'setz das', 'stelle das', 'das umsetzen',
    'setz es um', 'stelle es um', 'setz das bitte um', 'stelle das bitte um',
)
_PROVIDER_ALIASES = {
    'ollama': 'ollama', 'lokal': 'ollama', 'local': 'ollama',
    'openai_oauth': 'openai_oauth', 'oauth': 'openai_oauth', 'chatgpt': 'openai_oauth', 'codex': 'openai_oauth', 'login': 'openai_oauth',
    'openai': 'openai', 'openai-kompatibel': 'openai', 'openai_compat': 'openai', 'api-key': 'openai', 'apikey': 'openai',
}
_PRESET_ALIASES = {item: item for item in PRESET_IDS}
_PRESET_ALIASES.update({'lokales gateway': 'local', 'gateway': 'local'})
_KEY_ALIASES = {
    'anbieter': ('llm', 'provider'), 'provider': ('llm', 'provider'),
    'ersatzkette': ('llm', 'fallback_chain'), 'fallback': ('llm', 'fallback_chain'), 'fallback-kette': ('llm', 'fallback_chain'), 'fallback_chain': ('llm', 'fallback_chain'),
    'vorlage': ('llm', 'preset'), 'preset': ('llm', 'preset'),
    'modell': ('llm', 'model'), 'model': ('llm', 'model'),
    'basis-url': ('llm', 'base_url'), 'base_url': ('llm', 'base_url'),
    'ollama-url': ('llm', 'ollama_url'), 'ollama_url': ('llm', 'ollama_url'),
    'temperatur': ('llm', 'temperature'), 'temperature': ('llm', 'temperature'),
    'thema': ('ui', 'theme'), 'theme': ('ui', 'theme'),
    'sprache': ('ui', 'language'), 'language': ('ui', 'language'),
    'dichte': ('ui', 'density'), 'density': ('ui', 'density'),
    'animationen': ('ui', 'animations'), 'animations': ('ui', 'animations'),
    'http_port': ('network', 'http_port'), 'http-port': ('network', 'http_port'),
    'quic_port': ('network', 'quic_port'),
}


def parse_settings_intent(message: str) -> dict[str, Any] | None:
    text = str(message or '').strip()
    if not text:
        return None
    lowered = text.casefold()
    if any(marker in lowered for marker in _QUESTION_MARKERS) and not any(verb in lowered for verb in ('setze', 'stell', 'ändere', 'aendere')):
        return None
    if any(marker in lowered for marker in ('stell dich vor', 'wer bist du', 'erzähl mir', 'erzaehl mir', 'kennenlern')):
        return None
    if lowered.rstrip('.!') in _WORK_ONLY_PHRASES:
        return None
    explicit = any(verb in lowered for verb in _APPLY_VERBS) or any(phrase in lowered for phrase in _APPLY_PHRASES)
    if not explicit:
        return None
    if any(token in lowered for token in ('api-key', 'api key', 'api_key', 'schlüssel', 'schluessel')):
        return {'user_requested': True, 'error': 'API-Schlüssel setze ich nicht über den Chat. Nutze die Einstellungen; der Wert wird nie zurückgegeben.'}
    if not any(noun in lowered for noun in _SETTINGS_NOUNS):
        return None
    values_by_area: dict[str, dict[str, Any]] = {}
    chain = _parse_provider_chain(text)
    if chain is not None:
        if not chain:
            return {'user_requested': True, 'error': 'Ersatzkette ist leer oder ungültig. Nenne bekannte Anbieter ohne Duplikate, z. B. openai dann ollama.'}
        values_by_area.setdefault('llm', {})['fallback_chain'] = chain
    _extract_named_values(lowered, values_by_area)
    if 'llm' in values_by_area:
        _apply_preset_provider_hints(lowered, values_by_area['llm'])
    areas = [area for area, values in values_by_area.items() if values]
    if not areas:
        return {'user_requested': True, 'error': 'Ich habe den Änderungswunsch erkannt, aber keine gültigen Einstellungswerte gelesen.'}
    if len(areas) > 1:
        return {'user_requested': True, 'error': 'Bitte eine Settings-Area pro Auftrag, z. B. nur LLM oder nur Darstellung.'}
    area = areas[0]
    return {'user_requested': True, 'area': area, 'values': values_by_area[area], 'reason': 'Ausdrücklicher Nutzerwunsch im Chat'}


def _parse_provider_chain(text: str) -> list[str] | None:
    lowered = text.casefold()
    match = re.search(r'(ersatzkette|fallback(?:-|\s*)kette|fallback)\s+(?:auf|zu|:)\s+(.+)$', lowered)
    if not match:
        return None
    raw_parts = re.split(r'\s*(?:,|→|->|dann|danach|und dann|;|/)\s*', match.group(2).strip(' .'))
    chain: list[str] = []
    unknown: list[str] = []
    for part in raw_parts:
        token = part.strip().strip('.')
        if not token or token in {'bitte', 'und'}:
            continue
        mapped = _map_provider_token(token)
        if mapped is None:
            unknown.append(token)
            continue
        if mapped not in chain:
            chain.append(mapped)
    if unknown:
        return []
    return chain


def _map_provider_token(token: str) -> str | None:
    cleaned = token.strip().casefold().replace(' ', '_')
    if cleaned in PROVIDER_IDS:
        return cleaned
    if cleaned in _PROVIDER_ALIASES:
        return _PROVIDER_ALIASES[cleaned]
    if cleaned in _PRESET_ALIASES:
        return 'openai'
    return None


def _extract_named_values(lowered: str, values_by_area: dict[str, dict[str, Any]]) -> None:
    for alias, (area, key) in _KEY_ALIASES.items():
        match = re.search(rf'{re.escape(alias)}\s+(?:auf|zu|:)\s+([a-z0-9_.:/-]+)', lowered)
        if not match:
            continue
        raw = match.group(1).strip()
        value: Any = _coerce_value(area, key, raw)
        if value is None:
            continue
        values_by_area.setdefault(area, {})[key] = value


def _coerce_value(area: str, key: str, raw: str) -> Any:
    if key == 'provider':
        return _map_provider_token(raw)
    if key == 'preset':
        return _PRESET_ALIASES.get(raw, raw if raw in PRESET_IDS else None)
    if key == 'fallback_chain':
        return None
    enum_values = ENUM_RULES.get((area, key))
    if enum_values and raw in enum_values:
        return raw
    current_default = DEFAULT_SETTINGS.get(area, {}).get(key)
    if isinstance(current_default, bool):
        return raw in {'an', 'true', '1', 'ja', 'on'}
    if isinstance(current_default, int) and not isinstance(current_default, bool):
        return int(raw) if raw.isdigit() else None
    if isinstance(current_default, float):
        try:
            return float(raw)
        except ValueError:
            return None
    return raw


def _apply_preset_provider_hints(lowered: str, llm_values: dict[str, Any]) -> None:
    for preset in PRESET_IDS:
        if preset != 'custom' and preset in lowered:
            llm_values.setdefault('preset', preset)
            if llm_values.get('provider') in {None, 'ollama'}:
                if any(token in lowered for token in ('anbieter', 'provider', 'vorlage', 'preset', 'groq', 'openrouter', 'mistral', 'gemini')):
                    llm_values.setdefault('provider', 'openai')
