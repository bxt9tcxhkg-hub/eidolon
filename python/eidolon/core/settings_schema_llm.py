from __future__ import annotations

from typing import Any

from eidolon.core.config import DEFAULT_LLM_MODEL, OLLAMA_URL


def llm_defaults() -> dict[str, Any]:
    return {'model': DEFAULT_LLM_MODEL, 'provider': 'ollama', 'ollama_url': OLLAMA_URL, 'temperature': 0.7, 'max_tokens': 4096, 'system_prompt': 'Du bist Eidolon, ein autonomer KI-Assistent. Sei hilfreich, präzise und ehrlich.', 'fallback_chain': ['ollama', 'openai'], 'offline_mode': False, 'response_style': 'balanced'}


def llm_enum_rules() -> dict[tuple[str, str], set[str]]:
    return {('llm', 'provider'): {'ollama', 'openai', 'openai_oauth'}, ('llm', 'response_style'): {'concise', 'balanced', 'detailed', 'technical'}}


def llm_int_rules() -> dict[tuple[str, str], tuple[int, int]]:
    return {('llm', 'max_tokens'): (1, 200000)}


def llm_float_rules() -> dict[tuple[str, str], tuple[float, float]]:
    return {('llm', 'temperature'): (0.0, 2.0)}
