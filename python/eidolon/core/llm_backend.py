from __future__ import annotations

from typing import Any

from eidolon.core.llm_codex import complete_openai_oauth
from eidolon.core.llm_config_store import SYSTEM_PROMPT, load_llm_config, load_openai_api_key, save_llm_config, save_openai_api_key
from eidolon.core.llm_ollama import complete_ollama
from eidolon.core.llm_provider_status import codex_available as _codex_available, codex_login_status as _codex_login_status, get_ollama_models, get_openai_models, openai_connection_status


class LLMBackend:
    def __init__(self) -> None:
        cfg = load_llm_config()
        self.enabled = True
        self.model = cfg['model']
        self.provider = cfg['provider']
        self.ollama_url = cfg['ollama_url']

    def configure(self, **kwargs) -> None:
        cfg = save_llm_config(kwargs)
        self.model = cfg['model']
        self.provider = cfg['provider']
        self.ollama_url = cfg['ollama_url']
        self.enabled = True

    async def complete(self, system: str, user: str) -> str:
        if not self.enabled:
            raise RuntimeError('LLM-Backend ist deaktiviert.')
        if self.provider == 'openai_oauth':
            return complete_openai_oauth(self, system=system, user=user)
        if self.provider != 'ollama':
            raise RuntimeError(f'LLM-Provider nicht angebunden: {self.provider}')
        return complete_ollama(self, system=system, user=user)

    def status(self) -> dict[str, Any]:
        return {'model': self.model, 'provider': self.provider, 'ollama_url': self.ollama_url, 'openai': openai_connection_status()}


_backend: LLMBackend | None = None


def get_llm_backend() -> LLMBackend:
    global _backend
    if _backend is None:
        _backend = LLMBackend()
    return _backend
