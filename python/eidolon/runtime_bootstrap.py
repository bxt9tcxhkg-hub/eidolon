from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from eidolon.chat_runtime import build_chat_prompts, build_grounded_fallback_reply, build_runtime_context, finalize_chat_reply
from eidolon.core.capabilities import get_capability_registry
from eidolon.core.cert_manager import get_certificate_manager
from eidolon.core.config import HTTP_PORT, PROJECT_ROOT
from eidolon.operate.bridge import build_operate_snapshot, sync_operate_with_workspace_payload
from eidolon.runtime_lifecycle import build_lifespan, quic_runtime_status, start_runtime, stop_runtime
from eidolon.runtime_route_registry import register_routes
from eidolon.runtime_service_factory import RuntimeServices, create_runtime_services
from eidolon.runtime_support import self_reflect_candidates as runtime_self_reflect_candidates


class RuntimeApp:
    def __init__(self, project_root: Path = PROJECT_ROOT, namespace: Any | None = None):
        self.project_root = Path(project_root)
        self.namespace = namespace
        self.quic_server_state: dict[str, Any] = {'server': None}
        self.server_start = time.time()
        self.services: RuntimeServices = create_runtime_services(self.project_root)
        self.build_chat_prompts = build_chat_prompts
        self.build_grounded_fallback_reply = build_grounded_fallback_reply
        self.finalize_chat_reply = finalize_chat_reply
        self.app = self._create_app()
        self.health = self._register_routes()

    def _ns(self, name: str, fallback: Any) -> Any:
        return getattr(self.namespace, name, fallback) if self.namespace is not None else fallback

    def _create_app(self) -> FastAPI:
        app = FastAPI(title='Eidolon Central Agentic System', version='2.0.0', lifespan=build_lifespan(self))
        app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
        return app

    def _register_routes(self):
        return register_routes(self)

    async def start_runtime(self) -> None:
        await start_runtime(self)

    async def stop_runtime(self) -> None:
        await stop_runtime(self)

    def certificate_health(self) -> dict[str, Any]:
        cert_manager = self._ns('cert_manager', self.services.cert_manager)
        status = cert_manager.status()
        out = {
            'cert_exists': status.get('server_exists', False),
            'key_exists': status.get('server_exists', False),
            'ca_exists': status.get('ca_exists', False),
            'client_exists': status.get('client_exists', False),
            'cert_path': str(cert_manager.server_cert),
            'complete': status.get('complete', False),
        }
        if status.get('server_exists'):
            out.update({
                'subject': status.get('server_subject'),
                'issuer': status.get('server_issuer'),
                'not_after': status.get('server_not_after'),
                'days_left': status.get('server_days_left'),
                'sans': status.get('server_sans', []),
                'expired': status.get('server_expired', False),
            })
            try:
                out['chain_valid'] = cert_manager.verify_chain().get('ok', False)
            except Exception:
                out['chain_valid'] = False
        return out

    def quic_runtime_status(self) -> dict[str, Any]:
        return quic_runtime_status(self)

    def chat_runtime_payload(self, message: str, source: str, session: dict[str, Any] | None) -> dict[str, Any]:
        from eidolon.workspaces.message_candidate import capture_message_candidate
        workspace_ui = self._ns('workspace_ui_service', self.services.workspace_ui_service)
        if message:
            capture_message_candidate(workspace_ui, message, session, source=source)
        workspace_payload = workspace_ui.get_runtime_payload()
        capability_payload = get_capability_registry().list()
        user_model = self._ns('user_model_store', self.services.user_model_store).get()
        llm_backend = self._ns('llm_backend', self.services.llm_backend)
        llm_status = llm_backend.status()
        operate_service = self._ns('operate_service', self.services.operate_service)
        sync_fn = self._ns('sync_operate_with_workspace_payload', sync_operate_with_workspace_payload)
        sync_fn(operate_service, workspace_payload)
        build_snapshot = self._ns('build_operate_snapshot', build_operate_snapshot)
        operate_snapshot = build_snapshot(operate_service)
        context = build_runtime_context(message=message, session=session, source=source, workspace_payload=workspace_payload, llm_status=llm_status, capability_payload=capability_payload, user_model=user_model, operate_snapshot=operate_snapshot)
        from eidolon.core.runtime_problems import collect_visible_problems, health_visible_problems
        healing_state = {}
        try:
            healing_state = self._ns('healing_service', self.services.healing_service).get_state()
        except Exception:
            healing_state = {}
        certs = {}
        backup_stats = {}
        try:
            certs = self.certificate_health()
        except Exception:
            certs = {}
        try:
            backup_stats = self._ns('backup_service', self.services.backup_service).get_stats()
        except Exception:
            backup_stats = {}
        context['runtime_problems'] = collect_visible_problems(
            llm_status=llm_status,
            healing_state=healing_state,
            health_problems=health_visible_problems(certs=certs, backup_stats=backup_stats),
        )
        return context

    def self_reflect_candidates(self, limit: int = 5) -> list[dict[str, Any]]:
        return self_reflect_candidates_impl(limit)

    def self_reflect_candidates_impl(self, limit: int = 5) -> list[dict[str, Any]]:
        return runtime_self_reflect_candidates(self.project_root, self.services.code_analyzer, limit)


def build_runtime_app(project_root: Path = PROJECT_ROOT, namespace: Any | None = None) -> RuntimeApp:
    return RuntimeApp(project_root, namespace=namespace)
