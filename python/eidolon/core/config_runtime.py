from __future__ import annotations

import os


def int_env(name: str, default: int) -> int:
    return int(os.environ.get(name, str(default)))


HTTP_PORT = int_env('EIDOLON_HTTP_PORT', 8002)
QUIC_PORT = int_env('EIDOLON_QUIC_PORT', 4434)
MESH_DISCOVERY_PORT = int_env('EIDOLON_MESH_DISCOVERY_PORT', 8001)
OLLAMA_URL = os.environ.get('EIDOLON_OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('EIDOLON_OLLAMA_MODEL', 'llama3.1:8b')
DEFAULT_LLM_MODEL = os.environ.get('EIDOLON_LLM_MODEL', OLLAMA_MODEL)
QUIC_INSECURE_LOCAL_TEST = os.environ.get('EIDOLON_QUIC_INSECURE_LOCAL_TEST', '').lower() in {'1','true','yes'}
OPENAI_CLIENT_ID = os.environ.get('EIDOLON_OPENAI_CLIENT_ID', '')
OPENAI_CLIENT_SECRET = os.environ.get('EIDOLON_OPENAI_CLIENT_SECRET', '')
OPENAI_REDIRECT_URI_TEMPLATE = 'http://localhost:{http_port}/integrations/openai/callback'
HEALTH_CHECK_INTERVAL = 30
PAIRING_TTL_SECONDS = 300
FEATURES = {'llm_enabled': False, 'mesh_enabled': True, 'quic_enabled': True, 'overlay_enabled': False, 'websocket_enabled': True, 'browser_enabled': False, 'image_gen_enabled': False, 'tts_enabled': False}
