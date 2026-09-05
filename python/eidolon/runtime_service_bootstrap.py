from __future__ import annotations

from pathlib import Path

from eidolon.bots.role_registry import get_bot_role_registry
from eidolon.code_analysis_support import CodeAnalyzer
from eidolon.core.autonomy_engine import get_autonomy_engine
from eidolon.core.backup_service import get_backup_service
from eidolon.core.cert_manager import get_certificate_manager
from eidolon.core.config import HTTP_PORT, MESH_DISCOVERY_PORT
from eidolon.core.goal_deriver import GoalDeriver
from eidolon.core.healing import SelfHealingService
from eidolon.core.llm_backend import configure_from_settings, get_llm_backend
from eidolon.core.mesh_service import get_mesh_service
from eidolon.core.settings_store import SettingsStore
from eidolon.operate.service import get_operate_service
from eidolon.runtime_service_contracts import RuntimeServices
from eidolon.server_support import ChatSessionStore
from eidolon.user.topic_attention import TopicAttentionStore
from eidolon.user.user_model import UserModelStore
from eidolon.voice_runtime import VoiceRuntimeService
from eidolon.workspaces.project_analyzer import get_project_analyzer
from eidolon.workspaces.project_model import get_project_service
from eidolon.workspaces.workspace_service import get_workspace_service
from eidolon.workspaces.workspace_ui_service import get_workspace_ui_service


def configure_llm_backend(settings_store: SettingsStore):
    return configure_from_settings(settings_store.get_area('llm'), get_llm_backend())


def create_runtime_services(project_root: Path) -> RuntimeServices:
    settings_store = SettingsStore(project_root)
    return RuntimeServices(
        backup_service=get_backup_service(project_root),
        settings_store=settings_store,
        chat_session_store=ChatSessionStore(project_root),
        code_analyzer=CodeAnalyzer(project_root),
        mesh_service=get_mesh_service(project_root, HTTP_PORT, MESH_DISCOVERY_PORT),
        autonomy_engine=get_autonomy_engine(project_root),
        goal_deriver=GoalDeriver(project_root),
        cert_manager=get_certificate_manager(project_root),
        workspace_service=get_workspace_service(project_root),
        workspace_ui_service=get_workspace_ui_service(project_root),
        bot_role_registry=get_bot_role_registry(project_root),
        project_service=get_project_service(project_root),
        project_analyzer=get_project_analyzer(project_root),
        operate_service=get_operate_service(project_root),
        user_model_store=UserModelStore(project_root),
        topic_attention_store=TopicAttentionStore(project_root),
        llm_backend=configure_llm_backend(settings_store),
        healing_service=SelfHealingService(project_root, check_interval=30),
        voice_runtime_service=VoiceRuntimeService(project_root),
    )
