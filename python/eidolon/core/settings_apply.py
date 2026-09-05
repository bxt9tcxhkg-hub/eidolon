from __future__ import annotations

from typing import Any, Callable

from eidolon.core.llm_config_store import load_openai_api_key
from eidolon.core.llm_secrets import contains_secret
from eidolon.core.settings_schema import DEFAULT_SETTINGS

SECRET_SETTING_KEYS = {'api_key', 'openai_api_key', 'client_secret', 'secret', 'raw_key'}


def apply_user_settings(settings_store, request: dict[str, Any], *, after_llm: Callable[[], None] | None = None) -> dict[str, Any]:
    if not request.get('user_requested'):
        return {'ok': False, 'applied': False, 'error': 'Einstellungen ändere ich nur auf ausdrücklichen Wunsch, nicht stillschweigend.'}
    if request.get('error'):
        return {'ok': False, 'applied': False, 'error': str(request['error'])}
    area = str(request.get('area') or '').strip()
    if area not in DEFAULT_SETTINGS:
        return {'ok': False, 'applied': False, 'error': f'Unbekannter Einstellungsbereich: {area or "leer"}'}
    values = {key: value for key, value in dict(request.get('values') or {}).items() if key not in SECRET_SETTING_KEYS}
    if not values:
        return {'ok': False, 'applied': False, 'error': 'Keine anwendbaren Einstellungswerte erkannt. Schlüssel und Geheimnisse setze ich nicht über den Chat.'}
    result = settings_store.set_area(area, values)
    if not result.get('ok'):
        return {'ok': False, 'applied': False, 'area': area, 'error': result.get('error') or 'Einstellungen konnten nicht gespeichert werden.'}
    if area == 'llm' and after_llm is not None:
        after_llm()
    public = {
        'ok': True,
        'applied': True,
        'area': area,
        'updated': result.get('updated') or list(values.keys()),
        'settings': dict(settings_store.get_area(area)),
        'reason': request.get('reason') or 'Ausdrücklicher Nutzerwunsch',
    }
    for key in SECRET_SETTING_KEYS:
        public['settings'].pop(key, None)
    if contains_secret(repr(public), load_openai_api_key()):
        return {'ok': False, 'applied': False, 'error': 'Antwort würde ein Geheimnis enthalten und wurde unterdrückt.'}
    return public


def format_settings_apply_reply(result: dict[str, Any], llm_status: dict[str, Any] | None = None) -> str:
    if not result.get('ok'):
        return f'Einstellung nicht übernommen: {result.get("error") or "unbekannter Fehler"}.'
    updated = result.get('updated') or []
    area = result.get('area') or 'settings'
    bits = [f'Ich habe {area} auf deinen ausdrücklichen Wunsch geändert ({", ".join(str(item) for item in updated) or "keine Felder"}).']
    settings = result.get('settings') or {}
    if area == 'llm' and settings.get('fallback_chain'):
        bits.append('Ersatzkette: ' + ' → '.join(str(item) for item in settings['fallback_chain']) + '.')
    if area == 'ui' and settings.get('theme'):
        bits.append('Thema: ' + str(settings['theme']) + '.')
    connection = (llm_status or {}).get('connection') or {}
    if connection.get('detail'):
        bits.append(str(connection['detail']))
    problems = (llm_status or {}).get('problems') or []
    if problems:
        bits.append('Offene Hinweise: ' + '; '.join(str(item) for item in problems[:4]))
    bits.append('Es wurde kein Schlüsselwert zurückgegeben.')
    return ' '.join(bits)
