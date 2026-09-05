from __future__ import annotations

from typing import Any, Callable

from eidolon.core.llm_codex import complete_openai_oauth
from eidolon.core.llm_config_store import load_openai_api_key
from eidolon.core.llm_ollama import complete_ollama
from eidolon.core.llm_openai_compat import complete_openai_compat
from eidolon.core.llm_provider_catalog import PROVIDER_OLLAMA, PROVIDER_OPENAI_COMPAT, PROVIDER_OPENAI_OAUTH, build_fallback_chain
from eidolon.core.llm_secrets import redact_secrets


def complete_fns() -> dict[str, Callable[..., str]]:
    return {
        PROVIDER_OLLAMA: complete_ollama,
        PROVIDER_OPENAI_COMPAT: complete_openai_compat,
        PROVIDER_OPENAI_OAUTH: complete_openai_oauth,
    }


def complete_provider(backend, provider_id: str, *, system: str, user: str) -> str:
    complete_fn = complete_fns().get(provider_id)
    if complete_fn is None:
        raise RuntimeError(f'LLM-Provider nicht angebunden: {provider_id}')
    return complete_fn(backend, system=system, user=user)


def complete_with_fallback(backend, *, system: str, user: str) -> tuple[str, dict[str, Any]]:
    """Primary first, then unique remaining fallback_chain entries. Secrets stay out of errors."""
    chain = build_fallback_chain(getattr(backend, 'provider', PROVIDER_OLLAMA), getattr(backend, 'fallback_chain', None))
    errors: list[str] = []
    for provider_id in chain:
        try:
            text = complete_provider(backend, provider_id, system=system, user=user)
            return text, {'used_provider': provider_id, 'attempted': chain[: chain.index(provider_id) + 1], 'fallback_used': provider_id != chain[0]}
        except Exception as exc:
            errors.append(f'{provider_id}: {redact_secrets(str(exc), load_openai_api_key())}')
    joined = ' | '.join(errors) if errors else 'keine Provider'
    raise RuntimeError(f'Alle Provider der Ersatzkette sind fehlgeschlagen ({", ".join(chain)}). {joined}')
