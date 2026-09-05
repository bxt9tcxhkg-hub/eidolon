from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from eidolon.core.config import DATA_DIR, DEFAULT_LLM_MODEL, OLLAMA_URL

LLM_CONFIG_FILE = Path(DATA_DIR) / 'llm_config.json'
OPENAI_KEY_FILE = Path(DATA_DIR) / 'secrets' / 'openai_api_key'
LLM_CONFIG_KEYS = {
    'model', 'provider', 'ollama_url', 'base_url', 'preset',
    'auth_method', 'fallback_chain', 'temperature', 'max_tokens',
}
OLLAMA_MODELS = ['llama3.1:8b', 'llama3.1:70b', 'llama3:8b', 'mistral:7b', 'mixtral:8x7b', 'codellama:13b', 'codellama:34b', 'qwen2.5:7b', 'qwen2.5:14b', 'qwen2.5:32b', 'phi3:mini', 'phi3:medium', 'gemma2:9b', 'gemma2:27b']
OPENAI_MODELS = ['gpt-5.5', 'gpt-5', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-4o-mini', 'o1', 'o1-mini', 'o3-mini']
SYSTEM_PROMPT = (
    'Du bist Eidolon — das zentrale agentische Hauptsystem dieses Produkts. '
    'Du bist kein generischer Chat-Assistent, sondern der arbeitsführende Agent in einem laufenden Projekt- und Operate-Kontext. '
    'Führe Arbeit mit Struktur, Richtung, Empfehlung und konkreten nächsten Schritten voran. '
    'Wenn genug Kontext vorhanden ist, stelle keine generischen Hilfsrückfragen. '
    'Wenn etwas nicht möglich ist, sag es ehrlich. '
    'Erfinde keinen Projektzustand, keine Fähigkeiten und keine bereits erfolgte Ausführung.'
)


def default_llm_config() -> dict[str, Any]:
    return {
        'model': DEFAULT_LLM_MODEL,
        'provider': 'ollama',
        'ollama_url': OLLAMA_URL,
        'base_url': '',
        'preset': 'custom',
        'auth_method': 'none',
        'fallback_chain': ['ollama', 'openai'],
        'temperature': 0.7,
        'max_tokens': 4096,
    }


def load_llm_config() -> dict[str, Any]:
    default = default_llm_config()
    if not LLM_CONFIG_FILE.exists():
        return default
    try:
        data = json.loads(LLM_CONFIG_FILE.read_text(encoding='utf-8'))
        return {**default, **{key: value for key, value in data.items() if key in LLM_CONFIG_KEYS}}
    except Exception:
        return default


def save_llm_config(config: dict[str, Any]) -> dict[str, Any]:
    current = load_llm_config()
    current.update({key: value for key, value in config.items() if key in LLM_CONFIG_KEYS and value is not None})
    LLM_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LLM_CONFIG_FILE.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding='utf-8')
    return current


def save_openai_api_key(api_key: str) -> None:
    key = (api_key or '').strip()
    OPENAI_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not key:
        if OPENAI_KEY_FILE.exists():
            OPENAI_KEY_FILE.unlink()
        return
    OPENAI_KEY_FILE.write_text(key, encoding='utf-8')


def load_openai_api_key() -> str:
    env_key = os.environ.get('OPENAI_API_KEY', '').strip()
    if env_key:
        return env_key
    try:
        return OPENAI_KEY_FILE.read_text(encoding='utf-8').strip()
    except OSError:
        return ''
