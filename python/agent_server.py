#!/usr/bin/env python3
"""Eidolon central agentic system runtime."""
import sys
from typing import Any

from eidolon.core.backup_service import BackupService
from eidolon.core.config import HTTP_PORT, PROJECT_ROOT, migrate_legacy_state
from eidolon.operate.bridge import build_operate_snapshot
from eidolon.runtime_bootstrap import build_runtime_app
from eidolon.runtime_support import (
    BUILTIN_SKILLS,
    apply_llm_code_mutation as _apply_llm_code_mutation,
    latest_session_user_message as _latest_session_user_message,
    self_reflect_candidates as runtime_self_reflect_candidates,
)

migrate_legacy_state(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))


def _self_reflect_candidates(limit: int = 5) -> list[dict[str, Any]]:
    return runtime_self_reflect_candidates(PROJECT_ROOT, code_analyzer, limit)


runtime = build_runtime_app(PROJECT_ROOT, namespace=sys.modules[__name__])
app = runtime.app
health = runtime.health

backup_service = runtime.services.backup_service
settings_store = runtime.services.settings_store
chat_session_store = runtime.services.chat_session_store
code_analyzer = runtime.services.code_analyzer
mesh_service = runtime.services.mesh_service
autonomy_engine = runtime.services.autonomy_engine
goal_deriver = runtime.services.goal_deriver
cert_manager = runtime.services.cert_manager
workspace_service = runtime.services.workspace_service
workspace_ui_service = runtime.services.workspace_ui_service
bot_role_registry = runtime.services.bot_role_registry
project_service = runtime.services.project_service
project_analyzer = runtime.services.project_analyzer
operate_service = runtime.services.operate_service
user_model_store = runtime.services.user_model_store
topic_attention_store = runtime.services.topic_attention_store
llm_backend = runtime.services.llm_backend
healing_service = runtime.services.healing_service
voice_runtime_service = runtime.services.voice_runtime_service


def _spawn_openai_device_login() -> dict[str, Any]:
    return runtime.spawn_openai_device_login()


def _chat_runtime_payload(message: str, source: str, session: dict[str, Any] | None) -> dict[str, Any]:
    return runtime.chat_runtime_payload(message, source, session)


def _certificate_health() -> dict[str, Any]:
    return runtime.certificate_health()


def _quic_runtime_status() -> dict[str, Any]:
    return runtime.quic_runtime_status()


if __name__ == "__main__":
    import uvicorn

    print(f"Eidolon Agent Runtime startet auf Port {HTTP_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=HTTP_PORT)
