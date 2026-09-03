from __future__ import annotations


def extract_skill_name(text: str) -> str:
    text = str(text or '').lower()
    if any(k in text for k in ['modell', 'runtime', 'provider']):
        return 'runtime_facts'
    if any(k in text for k in ['system', 'info']):
        return 'system_info'
    if any(k in text for k in ['ziel', 'goal']):
        return 'goal_manager'
    if any(k in text for k in ['gerät', 'device', 'peer']):
        return 'device_status'
    if any(k in text for k in ['send', 'nachricht', 'mesh']):
        return 'mesh_send'
    if any(k in text for k in ['notiz', 'note']):
        return 'note'
    if any(k in text for k in ['datei', 'file']):
        return 'file_organizer'
    if any(k in text for k in ['kalender', 'calendar']):
        return 'calendar'
    return 'chat'
