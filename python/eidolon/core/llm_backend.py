from __future__ import annotations

from typing import Any

from eidolon.core.llm_config_store import SYSTEM_PROMPT, load_llm_config, load_openai_api_key, save_llm_config, save_openai_api_key
from eidolon.core.llm_connection import backend_status
from eidolon.core.llm_fallback import complete_with_fallback, iter_stream_or_complete, provider_can_stream
from eidolon.core.llm_provider_catalog import build_fallback_chain, normalize_llm_settings
from eidolon.core.llm_provider_status import codex_available as _codex_available, codex_login_status as _codex_login_status, get_ollama_models, get_openai_models, openai_connection_status


class LLMBackend:
    def __init__(self) -> None:
        self.enabled = True
        self._apply(load_llm_config())

    def _apply(self, cfg: dict[str, Any]) -> None:
        normalized, _changed = normalize_llm_settings(cfg)
        self.model = normalized['model']
        self.provider = normalized['provider']
        self.ollama_url = normalized['ollama_url']
        self.base_url = normalized.get('base_url') or ''
        self.preset = normalized.get('preset') or 'custom'
        self.auth_method = normalized.get('auth_method') or 'none'
        self.fallback_chain = list(normalized.get('fallback_chain') or ['ollama', 'openai'])
        self.temperature = float(normalized.get('temperature') or 0.7)
        self.max_tokens = int(normalized.get('max_tokens') or 4096)
        self.enabled = True

    def configure(self, **kwargs) -> None:
        self._apply(save_llm_config(kwargs))

    def can_stream(self) -> bool:
        if not self.enabled:
            return False
        chain = build_fallback_chain(self.provider, getattr(self, 'fallback_chain', None))
        return any(provider_can_stream(provider_id) for provider_id in chain)

    async def complete(self, system: str, user: str) -> str:
        if not self.enabled:
            raise RuntimeError('LLM-Backend ist deaktiviert.')
        text, _meta = complete_with_fallback(self, system=system, user=user)
        return text

    def iter_reply(self, system: str, user: str, *, prefer_stream: bool = False):
        if not self.enabled:
            raise RuntimeError('LLM-Backend ist deaktiviert.')
        if prefer_stream:
            yield from iter_stream_or_complete(self, system=system, user=user)
            return
        text, meta = complete_with_fallback(self, system=system, user=user)
        yield {'kind': 'complete', 'text': text, 'streamed': False, **meta}

    def status(self) -> dict[str, Any]:
        return backend_status(self)


def configure_from_settings(settings_area: dict[str, Any], backend: LLMBackend | None = None) -> LLMBackend:
    target = backend or get_llm_backend()
    keys = ('provider', 'model', 'ollama_url', 'base_url', 'preset', 'auth_method', 'fallback_chain', 'temperature', 'max_tokens')
    target.configure(**{key: settings_area[key] for key in keys if key in settings_area})
    return target


_backend: LLMBackend | None = None


def get_llm_backend() -> LLMBackend:
    global _backend
    if _backend is None:
        _backend = LLMBackend()
    return _backend
