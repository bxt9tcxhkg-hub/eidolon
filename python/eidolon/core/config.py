from __future__ import annotations

from eidolon.core.config_migration import migrate_legacy_state
from eidolon.core.config_paths import LEGACY_DATA_ROOT, LEGACY_PYTHON_DATA_DIR, PROJECT_ROOT, resolve_state_root, state_path
from eidolon.core.config_runtime import DEFAULT_LLM_MODEL, FEATURES, HEALTH_CHECK_INTERVAL, HTTP_PORT, MESH_DISCOVERY_PORT, OLLAMA_MODEL, OLLAMA_URL, OPENAI_CLIENT_ID, OPENAI_CLIENT_SECRET, OPENAI_REDIRECT_URI_TEMPLATE, PAIRING_TTL_SECONDS, QUIC_INSECURE_LOCAL_TEST, QUIC_PORT

STATE_ROOT = resolve_state_root()
DATA_DIR = STATE_ROOT
migrate_legacy_state(resolve_state_root, PROJECT_ROOT, PROJECT_ROOT)
GRAPH_DB = state_path('graph', 'knowledge.db')
EVIDENCE_DIR = state_path('evidence')
EVIDENCE_DB = state_path('evidence', 'evidence.db')
OPERATE_DIR = state_path('operate')
OPERATE_DB = state_path('operate', 'operate.db')
OPERATE_EVENTS_FILE = state_path('operate', 'events.jsonl')
CERT_DIR = state_path('mesh')
MESH_DIR = CERT_DIR
MESH_INBOX = state_path('mesh', 'mesh_inbox.json')
MESH_INBOX_DB = state_path('mesh', 'mesh_inbox.db')
MESH_PEERS_DB = state_path('mesh', 'peers.db')
HEALTH_DIR = state_path('healing')
HEALTH_LOG = state_path('healing', 'events.json')
USER_DIR = state_path('user')
AUTONOMY_DIR = state_path('autonomy')
PERSISTENCE_DIR = state_path('persistence')
AUTH_DIR = state_path('auth')
BACKUPS_DIR = state_path('backups')
LLM_CONFIG_FILE = state_path('llm_config.json')
CERT_FILE = CERT_DIR / 'server.crt'
KEY_FILE = CERT_DIR / 'server.key'
OPENAI_REDIRECT_URI = OPENAI_REDIRECT_URI_TEMPLATE.format(http_port=HTTP_PORT)
OPENAI_TOKEN_FILE = state_path('openai_token.json')
