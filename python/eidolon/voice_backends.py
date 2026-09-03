from __future__ import annotations

from typing import Any


def tts_backend_status() -> dict[str, Any]:
    try:
        import pyttsx3  # noqa: F401
        return {'available': True, 'provider': 'pyttsx3', 'mode': 'offline_local'}
    except Exception as exc:
        return {'available': False, 'provider': 'pyttsx3', 'reason': str(exc)}


def stt_backend_status() -> dict[str, Any]:
    try:
        import faster_whisper  # noqa: F401
        return {'available': True, 'provider': 'faster_whisper', 'mode': 'local_file_transcription', 'model': 'tiny', 'detail': 'Lokale Whisper-Transkription über faster_whisper'}
    except Exception:
        pass
    try:
        import speech_recognition  # noqa: F401
        return {'available': True, 'provider': 'speech_recognition', 'mode': 'local_file_or_mic'}
    except Exception:
        return {'available': False, 'provider': 'none', 'reason': 'Kein STT-Backend installiert (weder faster_whisper noch speech_recognition)'}
