from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from eidolon.core.evidence import get_evidence_store
from eidolon.core.config import state_path
from eidolon.voice_actions import record_stt_artifact, record_tts_artifact, transcribe_with_faster_whisper, transcribe_with_speech_recognition
from eidolon.voice_backends import stt_backend_status, tts_backend_status


class VoiceRuntimeService:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.output_dir = state_path('voice', project_root=self.project_root)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _tts_backend_status(self) -> dict[str, Any]: return tts_backend_status()
    def _stt_backend_status(self) -> dict[str, Any]: return stt_backend_status()
    def _transcribe_with_faster_whisper(self, source: Path) -> str: return transcribe_with_faster_whisper(source)
    def _transcribe_with_speech_recognition(self, source: Path) -> str: return transcribe_with_speech_recognition(self.output_dir, source)

    def status(self) -> dict[str, Any]:
        tts = self._tts_backend_status(); stt = self._stt_backend_status()
        return {'ok': True, 'tts': tts, 'stt': stt, 'degraded': not (tts.get('available') and stt.get('available')), 'checked_at': datetime.now(timezone.utc).isoformat()}

    def speak(self, text: str, voice: str | None = None, rate: int | None = None) -> dict[str, Any]:
        if not text or not text.strip():
            return {'ok': False, 'error': 'text is required'}
        backend = self._tts_backend_status()
        if not backend.get('available'):
            return {'ok': False, 'error': backend.get('reason') or 'TTS backend unavailable', 'tts': backend}
        import pyttsx3
        target = self.output_dir / f"tts_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}.wav"
        engine = pyttsx3.init()
        if voice:
            try: engine.setProperty('voice', voice)
            except Exception: pass
        if rate:
            try: engine.setProperty('rate', int(rate))
            except Exception: pass
        engine.save_to_file(text, str(target)); engine.runAndWait()
        if not target.exists() or target.stat().st_size <= 0:
            return {'ok': False, 'error': 'TTS erzeugte keine Audiodatei'}
        recorded = record_tts_artifact(text, target, backend)
        return {'ok': True, 'path': str(target), 'sha256': recorded['sha256'], 'size_bytes': recorded['size_bytes'], 'tts': backend, 'evidence': {'action_id': recorded['action_id'], 'status': 'verified'}}

    def transcribe(self, audio_path: str) -> dict[str, Any]:
        source = Path(audio_path); stt = self._stt_backend_status()
        if not source.exists():
            return {'ok': False, 'error': f'Audio file not found: {source}', 'stt': stt}
        if not stt.get('available'):
            evidence = get_evidence_store(); claim = f'STT transcription unavailable for {source.name}'
            evidence.log_blocked(claim=claim, reason=stt.get('reason') or 'STT backend unavailable', capability='voice:transcribe')
            return {'ok': False, 'error': stt.get('reason') or 'STT backend unavailable', 'stt': stt, 'blocked': True}
        try:
            provider = stt.get('provider')
            text = self._transcribe_with_faster_whisper(source) if provider == 'faster_whisper' else self._transcribe_with_speech_recognition(source) if provider == 'speech_recognition' else None
            if text is None:
                return {'ok': False, 'error': f'Nicht unterstütztes STT-Backend: {provider}', 'stt': stt}
        except Exception as exc:
            return {'ok': False, 'error': str(exc), 'stt': stt}
        return {'ok': True, 'text': text, 'stt': stt, 'evidence': record_stt_artifact(source, text)}


_service: VoiceRuntimeService | None = None


def get_voice_runtime_service(project_root: Path) -> VoiceRuntimeService:
    global _service
    if _service is None:
        _service = VoiceRuntimeService(project_root)
    return _service
