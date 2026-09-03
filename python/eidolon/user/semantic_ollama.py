from __future__ import annotations

from typing import Any


def check_ollama_embeddings() -> bool:
    try:
        import httpx
        response = httpx.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code != 200:
            return False
        models = response.json().get('models', [])
        return any('embed' in model.get('name', '').lower() for model in models)
    except Exception:
        return False


async def get_ollama_embeddings(texts: list[str]) -> list[list[float]] | None:
    if not check_ollama_embeddings():
        return None
    try:
        import httpx
        embeddings: list[list[float]] = []
        for text in texts:
            response = httpx.post(
                'http://localhost:11434/api/embeddings',
                json={'model': 'llama3.1:8b', 'prompt': text[:2000]},
                timeout=30,
            )
            if response.status_code != 200:
                return None
            embeddings.append(response.json().get('embedding', []))
        return embeddings if embeddings and all(embedding for embedding in embeddings) else None
    except Exception:
        return None
