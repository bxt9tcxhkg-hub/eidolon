from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from eidolon.code_analysis_support import CodeAnalyzer
from eidolon.core.goal_deriver import GoalDeriver
from eidolon.core.healing import SelfHealingService
from eidolon.core.settings_store import SettingsStore
from eidolon.server_support import ChatSessionStore
from eidolon.user.topic_attention import TopicAttentionStore
from eidolon.user.user_model import UserModelStore
from eidolon.voice_runtime import VoiceRuntimeService


@dataclass
class RuntimeServices:
    backup_service: Any
    settings_store: SettingsStore
    chat_session_store: ChatSessionStore
    code_analyzer: CodeAnalyzer
    mesh_service: Any
    autonomy_engine: Any
    goal_deriver: GoalDeriver
    cert_manager: Any
    workspace_service: Any
    workspace_ui_service: Any
    bot_role_registry: Any
    project_service: Any
    project_analyzer: Any
    operate_service: Any
    user_model_store: UserModelStore
    topic_attention_store: TopicAttentionStore
    llm_backend: Any
    healing_service: SelfHealingService
    voice_runtime_service: VoiceRuntimeService
