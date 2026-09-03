from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

from eidolon.core.evidence import get_evidence_store


def transcribe_with_faster_whisper(source: Path) -> str:
    from faster_whisper import WhisperModel
    model = WhisperModel('tiny', device='cpu', compute_type='int8')
    segments, _info = model.transcribe(str(source), language='de')
    text = ' '.join(segment.text.strip() for segment in segments).strip()
    if not text:
        raise RuntimeError('faster_whisper lieferte keinen Transkripttext')
    return text


def transcribe_with_speech_recognition(output_dir: Path, source: Path) -> str:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    prepared = source
    temp_copy = None
    if source.suffix.lower() == '.mp3':
        temp_copy = output_dir / f'{source.stem}_copy.wav'
        shutil.copyfile(source, temp_copy)
        prepared = temp_copy
    try:
        with sr.AudioFile(str(prepared)) as audio_file:
            audio = recognizer.record(audio_file)
        text = recognizer.recognize_sphinx(audio)
    finally:
        if temp_copy and temp_copy.exists():
            temp_copy.unlink(missing_ok=True)
    if not text:
        raise RuntimeError('speech_recognition lieferte keinen Transkripttext')
    return text


def record_tts_artifact(text: str, target: Path, backend: dict) -> dict:
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    evidence = get_evidence_store()
    action_id = evidence.log_action(command='voice:speak', exit_code=0, stdout=str({'text_preview': text[:80], 'path': str(target), 'provider': backend.get('provider')}), stderr=None)
    evidence.log_artifact(action_id, str(target), sha256=digest, size_bytes=target.stat().st_size)
    evidence.log_verification(action_id, 'TTS generated an audio artifact', 'verified', evidence=str({'path': str(target), 'sha256': digest}))
    return {'action_id': action_id, 'sha256': digest, 'size_bytes': target.stat().st_size}


def record_stt_artifact(source: Path, text: str) -> dict:
    evidence = get_evidence_store()
    action_id = evidence.log_action(command='voice:transcribe', exit_code=0, stdout=str({'audio_path': str(source), 'text_preview': text[:80]}), stderr=None)
    evidence.log_verification(action_id, 'STT produced transcript text', 'verified', evidence=str({'audio_path': str(source), 'text': text}))
    return {'action_id': action_id, 'status': 'verified'}
