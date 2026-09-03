from __future__ import annotations

from eidolon.autonomy_compat_routes import register_autonomy_compat_routes
from eidolon.certificate_routes import register_certificate_routes
from eidolon.chat_and_code_routes import register_chat_and_code_routes
from eidolon.core.autonomy_engine import CATEGORIES as GOAL_CATEGORIES
from eidolon.core.capabilities import get_capability_registry
from eidolon.core.config import HTTP_PORT, QUIC_PORT
from eidolon.core.llm_backend import SYSTEM_PROMPT, get_ollama_models, get_openai_models
from eidolon.healing_skills_routes import register_healing_skills_routes
from eidolon.identity_mesh_routes import register_identity_mesh_routes
from eidolon.mesh_pairing_routes import register_mesh_pairing_routes
from eidolon.operate.bridge import build_operate_snapshot, record_workspace_action, sync_operate_with_workspace_payload
from eidolon.operate_api_routes import register_operate_api_routes
from eidolon.project_routes import register_project_routes
from eidolon.runtime_health_routes import register_runtime_health_routes
from eidolon.runtime_service_factory import spawn_openai_device_login
from eidolon.runtime_support import BUILTIN_SKILLS, apply_llm_code_mutation, chat_runtime_truth_reply, human_duration, latest_session_user_message
from eidolon.settings_routes import register_settings_routes
from eidolon.system_status_routes import register_system_status_routes
from eidolon.web_routes import register_web_routes
from eidolon.workspace_routes import register_workspace_routes
from eidolon.workspaces.project_model import ProjectElement
from eidolon.backup_routes import register_backup_routes


def register_routes(runtime_app):
    register_web_routes(runtime_app.app, runtime_app.project_root)
    health = register_runtime_health_routes(
        runtime_app.app,
        get_server_start=lambda: runtime_app.server_start,
        get_autonomy_engine=lambda: runtime_app._ns('autonomy_engine', runtime_app.services.autonomy_engine),
        get_backup_service=lambda: runtime_app._ns('backup_service', runtime_app.services.backup_service),
        get_healing_service=lambda: runtime_app._ns('healing_service', runtime_app.services.healing_service),
        get_capability_registry=get_capability_registry,
        get_builtin_skills=lambda: BUILTIN_SKILLS,
        get_certificate_health=runtime_app.certificate_health,
        get_quic_runtime_status=runtime_app.quic_runtime_status,
        human_duration=human_duration,
        get_http_port=lambda: HTTP_PORT,
        get_quic_port=lambda: QUIC_PORT,
        project_root=runtime_app.project_root,
    )
    register_identity_mesh_routes(runtime_app.app, get_llm_backend=lambda: runtime_app._ns('llm_backend', runtime_app.services.llm_backend), get_bot_role_registry=lambda: runtime_app._ns('bot_role_registry', runtime_app.services.bot_role_registry), get_mesh_service=lambda: runtime_app._ns('mesh_service', runtime_app.services.mesh_service), get_http_port=lambda: HTTP_PORT)
    register_chat_and_code_routes(
        runtime_app.app,
        chat_session_store=runtime_app._ns('chat_session_store', runtime_app.services.chat_session_store),
        llm_backend=runtime_app._ns('llm_backend', runtime_app.services.llm_backend),
        settings_store=runtime_app._ns('settings_store', runtime_app.services.settings_store),
        topic_attention_store=runtime_app._ns('topic_attention_store', runtime_app.services.topic_attention_store),
        build_chat_prompts=runtime_app.build_chat_prompts,
        build_grounded_fallback_reply=runtime_app.build_grounded_fallback_reply,
        finalize_chat_reply=runtime_app.finalize_chat_reply,
        system_prompt=SYSTEM_PROMPT,
        chat_runtime_payload=lambda message, source, session: runtime_app.chat_runtime_payload(message, source, session),
        latest_session_user_message=latest_session_user_message,
        chat_runtime_truth_reply=lambda message: chat_runtime_truth_reply(message, runtime_app._ns('llm_backend', runtime_app.services.llm_backend)),
        self_reflect_candidates=lambda limit: runtime_app._ns('_self_reflect_candidates', runtime_app.self_reflect_candidates)(limit),
        apply_llm_code_mutation=lambda **kwargs: runtime_app._ns('_apply_llm_code_mutation', apply_llm_code_mutation)(**kwargs, project_root=runtime_app.project_root, llm_backend=runtime_app._ns('llm_backend', runtime_app.services.llm_backend), system_prompt=SYSTEM_PROMPT),
        code_analyzer=runtime_app._ns('code_analyzer', runtime_app.services.code_analyzer),
        project_root=runtime_app.project_root,
    )
    register_operate_api_routes(runtime_app.app, get_operate_service=lambda: runtime_app._ns('operate_service', runtime_app.services.operate_service), autonomy_engine=runtime_app._ns('autonomy_engine', runtime_app.services.autonomy_engine), goal_deriver=runtime_app._ns('goal_deriver', runtime_app.services.goal_deriver), workspace_ui_service=runtime_app._ns('workspace_ui_service', runtime_app.services.workspace_ui_service), health_callback=health, sync_operate_with_workspace_payload=sync_operate_with_workspace_payload, build_operate_snapshot=build_operate_snapshot, goal_categories=GOAL_CATEGORIES, autonomy_cycle_callback=None, llm_backend=runtime_app._ns('llm_backend', runtime_app.services.llm_backend))
    register_autonomy_compat_routes(runtime_app.app, get_autonomy_engine=lambda: runtime_app._ns('autonomy_engine', runtime_app.services.autonomy_engine), get_operate_service=lambda: runtime_app._ns('operate_service', runtime_app.services.operate_service), get_workspace_ui_service=lambda: runtime_app._ns('workspace_ui_service', runtime_app.services.workspace_ui_service), health_callback=health, goal_deriver=runtime_app._ns('goal_deriver', runtime_app.services.goal_deriver), goal_categories=GOAL_CATEGORIES, build_operate_snapshot=build_operate_snapshot)
    register_certificate_routes(runtime_app.app, get_cert_manager=lambda: runtime_app._ns('cert_manager', runtime_app.services.cert_manager))
    register_project_routes(runtime_app.app, get_project_service=lambda: runtime_app._ns('project_service', runtime_app.services.project_service), get_workspace_ui_service=lambda: runtime_app._ns('workspace_ui_service', runtime_app.services.workspace_ui_service), get_operate_service=lambda: runtime_app._ns('operate_service', runtime_app.services.operate_service), project_element_cls=ProjectElement, record_workspace_action=record_workspace_action)
    register_workspace_routes(runtime_app.app, get_workspace_ui_service=lambda: runtime_app._ns('workspace_ui_service', runtime_app.services.workspace_ui_service), get_workspace_service=lambda: runtime_app._ns('workspace_service', runtime_app.services.workspace_service))
    register_mesh_pairing_routes(runtime_app.app, get_mesh_service=lambda: runtime_app._ns('mesh_service', runtime_app.services.mesh_service), get_http_port=lambda: HTTP_PORT)
    register_settings_routes(runtime_app.app, get_settings_store=lambda: runtime_app._ns('settings_store', runtime_app.services.settings_store), reconfigure_llm=lambda: runtime_app.services.llm_backend.configure(provider=runtime_app._ns('settings_store', runtime_app.services.settings_store).get_area('llm').get('provider'), model=runtime_app._ns('settings_store', runtime_app.services.settings_store).get_area('llm').get('model'), ollama_url=runtime_app._ns('settings_store', runtime_app.services.settings_store).get_area('llm').get('ollama_url')))
    register_healing_skills_routes(runtime_app.app, project_root=runtime_app.project_root, get_healing_service=lambda: runtime_app._ns('healing_service', runtime_app.services.healing_service), get_builtin_skills=lambda: BUILTIN_SKILLS)
    register_system_status_routes(runtime_app.app, server_start=runtime_app.server_start, get_llm_backend=lambda: runtime_app._ns('llm_backend', runtime_app.services.llm_backend), get_settings_store=lambda: runtime_app._ns('settings_store', runtime_app.services.settings_store), get_workspace_ui_service=lambda: runtime_app._ns('workspace_ui_service', runtime_app.services.workspace_ui_service), get_voice_runtime_service=lambda: runtime_app._ns('voice_runtime_service', runtime_app.services.voice_runtime_service), get_ollama_models=get_ollama_models, get_openai_models=get_openai_models, get_openai_login_payload=lambda: runtime_app._ns('_spawn_openai_device_login', spawn_openai_device_login))
    register_backup_routes(runtime_app.app, project_root=runtime_app.project_root, get_backup_service=lambda: runtime_app._ns('backup_service', runtime_app.services.backup_service))
    return health
