# Eidolon Spec-to-System Mapping

> Status: evidence-backed mapping between the current Eidolon product specification and the current code/runtime state.
> This document describes **current fit**, **remaining mismatches**, and **priority order**. It does **not** claim the target model is fully complete.

## Fresh evidence basis
- `python/agent_server.py` → 70 lines
- `python/eidolon/runtime_bootstrap.py` → 102 lines
- `python/eidolon/runtime_service_factory.py` → 11 lines
- `python/eidolon/runtime_service_contracts.py` → 36 lines
- `python/eidolon/runtime_service_bootstrap.py` → 54 lines
- `python/eidolon/runtime_service_auth.py` → 23 lines
- `python/eidolon/runtime_lifecycle.py` → 80 lines
- `python/eidolon/runtime_route_registry.py` → 73 lines
- `python/eidolon/runtime_health_routes.py` → 54 lines
- `python/eidolon/runtime_health_payloads.py` → 16 lines
- `python/eidolon/runtime_health_system.py` → 35 lines
- `python/eidolon/identity_mesh_routes.py` → 94 lines
- `python/eidolon/backup_routes.py` → 65 lines
- `python/eidolon/settings_routes.py` → 77 lines
- `python/eidolon/healing_skills_routes.py` → 99 lines
- `python/eidolon/system_status_routes.py` → 69 lines
- `python/eidolon/llm_routes.py` → 98 lines
- `python/eidolon/chat_and_code_routes.py` → 34 lines
- `python/eidolon/chat_route_support.py` → 13 lines
- `python/eidolon/chat_session_routes.py` → 35 lines
- `python/eidolon/chat_message_routes.py` → 41 lines
- `python/eidolon/code_mutation_routes.py` → 52 lines
- `python/eidolon/operate_api_routes.py` → 34 lines
- `python/eidolon/operate_api_read_routes.py` → 74 lines
- `python/eidolon/operate_api_goal_routes.py` → 83 lines
- `python/eidolon/operate_api_action_routes.py` → 76 lines
- `python/eidolon/operate_api_helpers.py` → 29 lines
- `python/eidolon/autonomy_compat_routes.py` → 26 lines
- `python/eidolon/autonomy_compat_helpers.py` → 17 lines
- `python/eidolon/autonomy_compat_goal_routes.py` → 62 lines
- `python/eidolon/autonomy_compat_status.py` → 39 lines
- `python/eidolon/autonomy_compat_runtime_routes.py` → 60 lines
- `python/eidolon/certificate_routes.py` → 42 lines
- `python/eidolon/project_routes.py` → 114 lines
- `python/eidolon/project_route_support.py` → 107 lines
- `python/eidolon/workspace_routes.py` → 15 lines
- `python/eidolon/workspace_route_helpers.py` → 16 lines
- `python/eidolon/workspace_context_routes.py` → 52 lines
- `python/eidolon/workspace_mutation_routes.py` → 67 lines
- `python/eidolon/mesh_pairing_routes.py` → 88 lines
- `python/eidolon/mesh_pairing_support.py` → 35 lines
- `python/eidolon/code_analysis_support.py` → 41 lines
- `python/eidolon/core/mesh_service.py` → 150 lines
- `python/eidolon/core/mesh_support.py` → 23 lines
- `python/eidolon/core/mesh_models.py` → 42 lines
- `python/eidolon/core/mesh_discovery.py` → 86 lines
- `python/eidolon/core/mesh_crypto.py` → 42 lines
- `python/eidolon/core/mesh_pairing.py` → 88 lines
- `python/eidolon/core/mesh_rendering.py` → 81 lines
- `python/eidolon/core/backup_service.py` → 91 lines
- `python/eidolon/core/backup_models.py` → 13 lines
- `python/eidolon/core/backup_catalog.py` → 16 lines
- `python/eidolon/core/backup_utils.py` → 40 lines
- `python/eidolon/core/backup_actions.py` → 41 lines
- `python/eidolon/core/auth.py` → 31 lines
- `python/eidolon/core/auth_models.py` → 5 lines
- `python/eidolon/core/auth_roles.py` → 35 lines
- `python/eidolon/core/auth_hashing.py` → 36 lines
- `python/eidolon/core/auth_entities.py` → 80 lines
- `python/eidolon/core/auth_store.py` → 33 lines
- `python/eidolon/core/auth_store_support.py` → 49 lines
- `python/eidolon/core/auth_store_rows.py` → 20 lines
- `python/eidolon/core/auth_store_users.py` → 56 lines
- `python/eidolon/core/auth_store_keys.py` → 21 lines
- `python/eidolon/core/auth_manager.py` → 84 lines
- `python/eidolon/core/auth_logic.py` → 18 lines
- `python/eidolon/core/auth_rate_limiter.py` → 29 lines
- `python/eidolon/core/auth_user_ops.py` → 62 lines
- `python/eidolon/core/auth_session_ops.py` → 32 lines
- `python/eidolon/core/auth_api_key_ops.py` → 47 lines
- `python/eidolon/core/autonomy_engine.py` → 26 lines
- `python/eidolon/core/autonomy_models.py` → 105 lines
- `python/eidolon/core/autonomy_runtime.py` → 79 lines
- `python/eidolon/core/autonomy_store.py` → 49 lines
- `python/eidolon/core/autonomy_goal_ops.py` → 6 lines
- `python/eidolon/core/autonomy_goal_mutations.py` → 5 lines
- `python/eidolon/core/autonomy_goal_goal_ops.py` → 47 lines
- `python/eidolon/core/autonomy_goal_step_ops.py` → 51 lines
- `python/eidolon/core/autonomy_goal_transition_ops.py` → 39 lines
- `python/eidolon/core/autonomy_goal_queries.py` → 81 lines
- `python/eidolon/core/autonomy_verifier.py` → 58 lines
- `python/eidolon/core/cert_manager.py` → 66 lines
- `python/eidolon/core/cert_paths.py` → 17 lines
- `python/eidolon/core/cert_status.py` → 51 lines
- `python/eidolon/core/cert_generation.py` → 80 lines
- `python/eidolon/core/cert_verify.py` → 28 lines
- `python/eidolon/core/llm_backend.py` → 57 lines
- `python/eidolon/core/llm_config_store.py` → 78 lines
- `python/eidolon/core/llm_provider_catalog.py` → 123 lines
- `python/eidolon/core/llm_secrets.py` → 65 lines
- `python/eidolon/core/llm_openai_compat.py` → 60 lines
- `python/eidolon/core/llm_fallback.py` → 39 lines
- `python/eidolon/core/llm_connection.py` → 60 lines
- `python/eidolon/core/llm_provider_status.py` → 46 lines
- `python/eidolon/core/llm_codex.py` → 42 lines
- `python/eidolon/core/llm_ollama.py` → 20 lines
- `python/eidolon/core/settings_store.py` → 88 lines
- `python/eidolon/core/settings_store_helpers.py` → 70 lines
- `python/eidolon/core/settings_persistence.py` → 28 lines
- `python/eidolon/core/settings_meta.py` → 24 lines
- `python/eidolon/core/settings_mutations.py` → 38 lines
- `python/eidolon/core/settings_schema.py` → 9 lines
- `python/eidolon/core/settings_schema_network.py` → 15 lines
- `python/eidolon/core/settings_schema_llm.py` → 40 lines
- `python/eidolon/core/settings_schema_autonomy.py` → 15 lines
- `python/eidolon/core/settings_schema_mesh.py` → 21 lines
- `python/eidolon/core/settings_schema_surfaces.py` → 18 lines
- `python/eidolon/core/settings_schema_builders.py` → 27 lines
- `python/eidolon/core/settings_validation.py` → 51 lines
- `python/eidolon/core/settings_validation_support.py` → 155 lines
- `python/eidolon/core/capabilities.py` → 16 lines
- `python/eidolon/core/capability_checks.py` → 54 lines
- `python/eidolon/core/capability_models.py` → 61 lines
- `python/eidolon/core/capability_catalog.py` → 24 lines
- `python/eidolon/operate/store.py` → 15 lines
- `python/eidolon/operate/store_foundation.py` → 34 lines
- `python/eidolon/operate/store_connection.py` → 9 lines
- `python/eidolon/operate/store_schema.py` → 7 lines
- `python/eidolon/operate/store_schema_fragments.py` → 126 lines
- `python/eidolon/operate/store_session_updates.py` → 25 lines
- `python/eidolon/operate/store_run_state.py` → 13 lines
- `python/eidolon/operate/store_run_records.py` → 49 lines
- `python/eidolon/operate/store_run_blocking.py` → 43 lines
- `python/eidolon/operate/store_run_evidence.py` → 34 lines
- `python/eidolon/operate/store_session_objective.py` → 87 lines
- `python/eidolon/operate/store_rows.py` → 58 lines
- `python/eidolon/operate/contract_records.py` → 6 lines
- `python/eidolon/operate/contract_session_records.py` → 22 lines
- `python/eidolon/operate/contract_run_records.py` → 41 lines
- `python/eidolon/operate/contract_blocking_records.py` → 29 lines
- `python/eidolon/operate/contract_evidence_records.py` → 36 lines
- `python/eidolon/operate/service.py` → 86 lines
- `python/eidolon/operate/service_objectives.py` → 58 lines
- `python/eidolon/operate/service_support.py` → 19 lines
- `python/eidolon/operate/service_support_common.py` → 20 lines
- `python/eidolon/operate/service_support_state.py` → 46 lines
- `python/eidolon/operate/service_support_actions.py` → 72 lines
- `python/eidolon/operate/bridge.py` → 5 lines
- `python/eidolon/operate/bridge_snapshot.py` → 29 lines
- `python/eidolon/operate/bridge_sync.py` → 28 lines
- `python/eidolon/operate/bridge_actions.py` → 25 lines
- `python/eidolon/operate/bridge_workspace.py` → 29 lines
- `python/eidolon/operate/bridge_workspace_bootstrap.py` → 62 lines
- `python/eidolon/operate/bridge_workspace_transitions.py` → 46 lines
- `python/eidolon/operate/bridge_views.py` → 54 lines
- `python/eidolon/chat_runtime.py` → 16 lines
- `python/eidolon/chat_runtime_patterns.py` → 57 lines
- `python/eidolon/chat_runtime_context.py` → 16 lines
- `python/eidolon/chat_runtime_prompting.py` → 26 lines
- `python/eidolon/chat_runtime_quality.py` → 5 lines
- `python/eidolon/chat_quality_checks.py` → 25 lines
- `python/eidolon/chat_quality_fallbacks.py` → 57 lines
- `python/eidolon/chat_quality_finalize.py` → 19 lines
- `python/eidolon/work_context_kernel.py` → 33 lines
- `python/eidolon/work_context_support.py` → 78 lines
- `python/eidolon/work_context_intent.py` → 78 lines
- `python/eidolon/work_context_builder.py` → 29 lines
- `python/eidolon/work_context_projection.py` → 96 lines
- `python/eidolon/work_context_contracts.py` → 65 lines
- `python/eidolon/workspaces/workspace_ui_service.py` → 97 lines
- `python/eidolon/workspaces/workspace_payloads.py` → 58 lines
- `python/eidolon/workspaces/workspace_payload_records.py` → 16 lines
- `python/eidolon/workspaces/workspace_payload_assistance.py` → 71 lines
- `python/eidolon/workspaces/workspace_payload_context.py` → 34 lines
- `python/eidolon/workspaces/workspace_payload_views.py` → 15 lines
- `python/eidolon/workspaces/workspace_actions.py` → 24 lines
- `python/eidolon/workspaces/workspace_action_support.py` → 28 lines
- `python/eidolon/workspaces/workspace_action_mutations.py` → 58 lines
- `python/eidolon/workspaces/workspace_action_evidence.py` → 18 lines
- `python/eidolon/workspaces/domain_engine.py` → 50 lines
- `python/eidolon/workspaces/domain_engine_tasks.py` → 51 lines
- `python/eidolon/workspaces/domain_engine_mutations.py` → 62 lines
- `python/eidolon/workspaces/domain_engine_views.py` → 17 lines
- `python/eidolon/workspaces/domain_models.py` → 5 lines
- `python/eidolon/workspaces/domain_rules.py` → 33 lines
- `python/eidolon/workspaces/domain_time.py` → 15 lines
- `python/eidolon/workspaces/domain_task.py` → 89 lines
- `python/eidolon/workspaces/domain_store.py` → 34 lines
- `python/eidolon/workspaces/domain_analysis.py` → 72 lines
- `python/eidolon/workspaces/project_analyzer.py` → 32 lines
- `python/eidolon/workspaces/project_analyzer_roadmap.py` → 27 lines
- `python/eidolon/workspaces/project_analyzer_modules.py` → 15 lines
- `python/eidolon/workspaces/project_analyzer_stats.py` → 26 lines
- `python/eidolon/workspaces/workspace_service.py` → 49 lines
- `python/eidolon/workspaces/workspace_service_support.py` → 25 lines
- `python/eidolon/workspaces/workspace_service_tasks.py` → 13 lines
- `python/eidolon/workspaces/project_support.py` → 35 lines
- `python/eidolon/workspaces/workspace_support.py` → 4 lines
- `python/eidolon/workspaces/workspace_support_summary.py` → 49 lines
- `python/eidolon/workspaces/workspace_support_projection.py` → 76 lines
- `python/eidolon/workspaces/state.py` → 71 lines
- `python/eidolon/workspaces/state_support.py` → 92 lines
- `python/eidolon/workspaces/state_contracts.py` → 12 lines
- `python/eidolon/workspaces/module_runtime.py` → 39 lines
- `python/eidolon/workspaces/module_runtime_support.py` → 49 lines
- `python/eidolon/workspaces/module_runtime_actions.py` → 75 lines
- `python/eidolon/workspaces/module_runtime_actions_board.py` → 60 lines
- `python/eidolon/workspaces/module_runtime_actions_graph.py` → 33 lines
- `python/eidolon/workspaces/module_runtime_actions_misc.py` → 70 lines
- `python/eidolon/workspaces/orchestrator.py` → 31 lines
- `python/eidolon/workspaces/orchestrator_support.py` → 18 lines
- `python/eidolon/workspaces/orchestrator_candidates.py` → 79 lines
- `python/eidolon/workspaces/registry.py` → 67 lines
- `python/eidolon/workspaces/registry_support.py` → 18 lines
- `python/eidolon/workspaces/registry_proposals.py` → 34 lines
- `python/eidolon/mesh/peers.py` → 49 lines
- `python/eidolon/mesh/inbox.py` → 86 lines
- `python/eidolon/mesh/inbox_support.py` → 45 lines
- `python/eidolon/core/mesh_service.py` → 57 lines
- `python/eidolon/core/mesh_identity.py` → 26 lines
- `python/eidolon/core/mesh_peer_views.py` → 29 lines
- `python/eidolon/core/mesh_pairing_service.py` → 34 lines
- `python/eidolon/mesh/mesh_handler.py` → 66 lines
- `python/eidolon/mesh/mesh_handler_support.py` → 19 lines
- `python/eidolon/mesh/mesh_handler_messages.py` → 28 lines
- `python/eidolon/mesh/mesh_handler_runtime.py` → 26 lines
- `python/eidolon/mesh/peer_models.py` → 32 lines
- `python/eidolon/mesh/peer_store_support.py` → 29 lines
- `python/eidolon/mesh/peer_queries.py` → 32 lines
- `python/eidolon/mesh/peer_mutations.py` → 41 lines
- `python/eidolon/mesh/transport/quic_server.py` → 85 lines
- `python/eidolon/mesh/transport/quic_protocol.py` → 23 lines
- `python/eidolon/mesh/transport/quic_cert_config.py` → 32 lines
- `python/eidolon/mesh/transport/quic_threading.py` → 16 lines
- `python/eidolon/skills/registry.py` → 91 lines
- `python/eidolon/skills/skill_types.py` → 17 lines
- `python/eidolon/skills/skill_state.py` → 15 lines
- `python/eidolon/skills/skill_catalog.py` → 32 lines
- `python/eidolon/skills/skill_routing.py` → 20 lines
- `python/eidolon/ui/hud.py` → 81 lines
- `python/eidolon/ui/hud_support.py` → 14 lines
- `python/eidolon/ui/hud_render.py` → 17 lines
- `python/eidolon/browser_control.py` → 59 lines
- `python/eidolon/browser_control_models.py` → 21 lines
- `python/eidolon/browser_control_sessions.py` → 34 lines
- `python/eidolon/browser_control_actions.py` → 54 lines
- `python/eidolon/user/proactive_assistance.py` → 82 lines
- `python/eidolon/user/proactive_policy.py` → 26 lines
- `python/eidolon/user/proactive_scoring.py` → 47 lines
- `python/eidolon/user/proactive_visibility.py` → 20 lines
- `python/eidolon/core/evidence.py` → 60 lines
- `python/eidolon/core/evidence_store_support.py` → 57 lines
- `python/eidolon/core/evidence_logging.py` → 40 lines
- `python/eidolon/core/evidence_queries.py` → 24 lines
- `python/eidolon/core/healing.py` → 70 lines
- `python/eidolon/core/healing_log.py` → 15 lines
- `python/eidolon/core/healing_checks.py` → 18 lines
- `python/eidolon/core/healing_runtime.py` → 46 lines
- `python/eidolon/core/healing_loop.py` → 9 lines
- `python/eidolon/voice_runtime.py` → 74 lines
- `python/eidolon/voice_backends.py` → 18 lines
- `python/eidolon/voice_actions.py` → 42 lines
- `python/eidolon/core/config.py` → 32 lines
- `python/eidolon/core/config_paths.py` → 36 lines
- `python/eidolon/core/config_runtime.py` → 18 lines
- `python/eidolon/core/config_migration.py` → 51 lines
- `python/eidolon/user/semantic_clustering.py` → 67 lines
- `python/eidolon/user/semantic_clustering_algorithms.py` → 42 lines
- `python/eidolon/user/semantic_clustering_views.py` → 17 lines
- `python/eidolon/user/semantic_utils.py` → 91 lines
- `python/eidolon/user/semantic_ollama.py` → 27 lines
- `python/eidolon/user/topic_attention.py` → 90 lines
- `python/eidolon/user/topic_attention_analysis.py` → 12 lines
- `python/eidolon/user/topic_attention_constants.py` → 31 lines
- `python/eidolon/user/topic_attention_extractors.py` → 31 lines
- `python/eidolon/user/topic_attention_topics.py` → 68 lines
- `python/eidolon/user/topic_attention_sources.py` → 15 lines
- `python/eidolon/bots/role_registry.py` → 63 lines
- `python/eidolon/bots/role_registry_store.py` → 52 lines
- `python/eidolon/bots/role_registry_ops.py` → 58 lines
- `python/eidolon/bots/role_models.py` → 47 lines
- `python/eidolon/bots/role_catalog.py` → 80 lines
- `python/eidolon/bots/role_validation.py` → 77 lines
- `python/eidolon/server_support.py` → 7 lines
- `python/eidolon/server_backups.py` → 85 lines
- `python/eidolon/server_backups_catalog.py` → 15 lines
- `python/eidolon/server_backups_files.py` → 40 lines
- `python/eidolon/server_backups_views.py` → 21 lines
- `python/eidolon/server_chat_sessions.py` → 50 lines
- `python/eidolon/server_chat_session_models.py` → 18 lines
- `python/eidolon/server_chat_session_store.py` → 20 lines
- `python/eidolon/server_chat_session_views.py` → 38 lines
- `python/eidolon/server_code_analysis.py` → 44 lines
- `python/eidolon/web_routes.py` → 68 lines
- `python/eidolon/web/index.html` → 6 lines
- `python/eidolon/web/fragments/index-head.html` → 61 lines
- `python/eidolon/web/fragments/index-operate-chat-dashboard.html` → 160 lines
- `python/eidolon/web/fragments/index-workspaces-goals.html` → 302 lines
- `python/eidolon/web/fragments/index-healing-footer.html` → 103 lines
- `python/eidolon/web/pairing-page.html` → 186 lines
- `python/eidolon/web/app-shell.css` → 171 lines
- `python/eidolon/web/app-components.css` → 3 lines
- `python/eidolon/web/components/app-components-base.css` → 118 lines
- `python/eidolon/web/components/app-components-chat.css` → 171 lines
- `python/eidolon/web/components/app-components-goals.css` → 394 lines
- `python/eidolon/web/app-canvas.css` → 187 lines
- `python/eidolon/web/app-mobile.css` → 83 lines
- `python/eidolon/web/app-shell.js` → 219 lines
- `python/eidolon/web/chat-ui.js` → 538 lines
- `python/eidolon/web/dashboard-ui.js` → 176 lines
- `python/eidolon/web/goals-ui.js` → 164 lines
- `python/eidolon/web/admin-ui.js` → 27 lines
- `python/eidolon/web/code-repair-ui.js` → 47 lines
- `python/eidolon/web/healing-ui.js` → 25 lines
- `python/eidolon/web/skills-backups-ui.js` → 81 lines
- `python/eidolon/web/settings-ui.js` → 303 lines
- `python/eidolon/web/workspace-ui.js` → 82 lines
- `python/eidolon/web/workspace-project-ui.js` → 377 lines
- `python/eidolon/web/workspace-canvas-ui.js` → 144 lines
- `python/eidolon/web/workspace-views-ui.js` → 86 lines
- `python/eidolon/web/workspace-element-composer-ui.js` → 115 lines
- `python/eidolon/web/operate-ui.js` → 13 lines
- `python/eidolon/web/operate-render-ui.js` → 94 lines
- `python/eidolon/web/operate-actions-ui.js` → 43 lines
- `python/eidolon/web/operate-view-ui.js` → 61 lines
- live app object → 162 routes
- live route path+method duplicates → 0
- live `GET /identity` → returns `product_role: "Zentrales agentisches Hauptsystem"`
- live `GET /chat/context` → returns runtime context including chat/workspace/operate state
- live `python -m pytest -q` → passes for formation/board-card-quality/Freigabe and prior contracts (152 passed, 2 warnings); this Cloud-Agent environment additionally failed 5 pre-existing checks: no live Ollama (`test_chat_endpoint_returns_real_model_response`), missing `aioquic`, `oauth_supported is False` without Codex CLI (2 tests), and a stale Chat-header copy assert from an earlier idle-copy change. `EIDOLON_STATE_DIR` collapses tmp_path stores; tests here used `LOCALAPPDATA=/tmp/AppData/Local`.
- repo runtime-state roots `python/data/` and `data/` → removed from the repo
- active runtime-state root → `%LOCALAPPDATA%/Eidolon/state/`

## Executive verdict
The direction is materially stronger than before:
- product identity is now explicit in runtime and UI
- chat no longer depends on generic-assistant first reactions
- role truth separates `active` from `defined`
- operate state is a real product kernel, not just a UI idea

The system is **not yet fully unified** because:
- documentation had drift and needed consolidation
- runtime-state truth is now centralized externally, but some secondary/historical docs still refer to old repo-local state paths
- Chat/Operate/Projektfläche now share `work_kernel` + Operate snapshot on read and on project mutations; board-element blockers remain a second persisted model next to Operate blockers
- some structural concentration remains, but the latest QUIC, healing, backups, browser-control, settings-schema, mesh-service, and operate-record hot spots were split into narrower modules
- several runtime values were broader than the typed operate contracts admitted (subagent function families and evidence kinds), so the contracts needed truth hardening to match live behavior
- the former workspace/domain/runtime/mesh hot spots were split into smaller files without changing the live UI/API contracts
- role registry, autonomy runtime, project model, chat runtime, server support, operate API routes, certificate handling, backup handling, LLM backend plumbing, user topic clustering, autonomy compat routes, workspace routes, peer persistence, module runtime, settings, evidence, auth logic, auth store, workspace state/actions, registry, voice runtime, HUD, health routes, mesh service, QUIC transport, healing, browser control, and operate records now follow narrower file boundaries while preserving runtime contracts

## Fit by area
- Product identity: **7/10**
- Core workflow: **7/10**
- Project formation: **8/10**
- Autonomy contract: **6/10**
- Bot organization: **8/10**
- UI/workspace architecture: **7/10**
- Truth/verification hygiene: **7/10**
- Maintainability: **4/10**

## Area 1 — Product identity
### Spec target
Eidolon is the central agentic main system, not primarily a generic assistant or a feature collection.

### Current evidence
- `/identity` now reports `product_role: "Zentrales agentisches Hauptsystem"`
- `agent_server.py` app title is `Eidolon Central Agentic System`
- sidebar header and chat entry reflect central-product language

### Remaining mismatch
- older historical docs still exist in the repo and can be misread without boundary discipline
- some root technical docs previously foregrounded runtime/mesh over product logic

### Verdict
**Mostly aligned, but requires disciplined documentation hierarchy.**

## Area 2 — Core workflow
### Spec target
Chat is fixed entry; Eidolon understands, structures, classifies, organizes, executes, verifies, and continues.

### Current evidence
- chat is the active initial panel
- chat runtime compiles context and enforces a brief cowork reply (max ~3–5 lines, one next action or one question, board over catalog)
- operate snapshot provides run/objective/blocker/approval/evidence state
- `/chat/context` exposes pending approvals, open blockers, and next_action for Chat execute actions

### Remaining mismatch
- the full conversation→operate→workspace loop is still distributed across several modules rather than one explicit kernel boundary

### Verdict
**Real partial alignment with remaining architectural split.**

## Area 3 — Project formation
### Current evidence
- workspace payloads expose `product_state` such as `project_candidate` and `active_project`
- chat runtime reacts differently to active project, candidate project, and no live context
- `python/eidolon/workspaces/project_formation.py` is the public transition contract (`chat_topic` → `project_candidate` → `active_project`)
- `POST /workspaces/formation` persists the transition; `project_candidate` → `active_project` requires `confirmed=true` and may create a real project
- Chat shows the pending transition (`#chat-formation`) and calls the same formation API
- heuristic mapping no longer silent-promotes runtime `active` to `active_project`
- work-oriented chat messages persist a visible `project_candidate` without an LLM; confirm seeds generic, constraint-aware board cards from the Vorhaben text and may request a real Operate approval for booking/external-write steps
- board seed is idempotent (`seed:vorhaben` + `slot:*`); user-owned cards are not duplicated or rewritten

### Remaining mismatch
- first-hop title/summary extraction is deterministic, not model-enriched
- Operate `context_kind` is updated on confirmed transitions, but not every historical session is backfilled
- Freigaben are created only for consequential external/booking-class steps, not for every next_step

### Verdict
**Canonical transition contract is visible in Chat without Ollama; confirm fills the board and can open a real Freigabe door.**

## Area 4 — Autonomy and approval
### Current evidence
- operate contracts model approvals, blockers, interruptions, next actions
- role registry enforces explicit approval for persistent approved roles

### Remaining mismatch
- Arbeit shows Freigeben/Ablehnen when a pending gate exists; Chat keeps the same APIs during an active turn, without an idle Freigabe-Dashboard
- Interrupts are still a thinner path than approvals

### Verdict
**Approval door is wired for pending gates and consequential external-write steps; not every next step invents a Freigabe.**

## Area 5 — Bot organization
### Current evidence
- `/identity` and role registry distinguish active roles from defined templates
- templates are not falsely presented as live operators

### Verdict
**Strong improvement and currently one of the better-aligned areas.**

## Area 6 — UI/workspace architecture
### Current evidence
- idle Chat is a door: session title + composer, plus one project line when an active project exists
- certificate/healing diagnostics stay on Systemstatus/Stabilität/Mehr, not in the chat transcript
- operate page (`#operate`) shows approvals, blockers, subagents, evidence, next action, history, work graph
- operate is reachable from nav, but `/` and empty hash still open Chat
- project work surface defaults to a generic planning board with kernel-fed slots; no domain packs
- idle Projektfläche leads with Neues Projekt + empty board and hides the Operate overview wall
- idle Arbeit offers Chat start, optional project takeover, and a short hint instead of an empty section wall
- action motion confirms real mutations only and honors reduced-motion plus `ui.animations`
- dark shell uses warmer neutrals and a richer accent; idle Chat stays title + composer
- work-trace lines on Arbeit and Projektfläche read operate/session signals and otherwise show a calm ready state

### Remaining mismatch
- the root component stylesheet is now segmented, but the goals component slice remains comparatively large
- primary nav is Chat / Projektfläche / Arbeit; utilities are grouped under Betrieb and Technik
- generic slots are kernel-fed and denser, still not a full adaptive composition engine

### Verdict
**Semantically improved; interaction grammar is thinner on the primary surfaces, with remaining density in utility and goals CSS.**

## Area 7 — Maintainability
### Current evidence
- active code passes tests
- repo no longer contains active runtime-state directories `python/data/` or `data/`
- runtime-state is resolved centrally via `eidolon.core.config.state_path(...)`
- previous runtime/product hotspots (`workspace_payloads.py`, `bridge_workspace.py`, `service_support.py`, `runtime_support.py`, `runtime_service_factory.py`, `auth_logic.py`, `module_runtime_actions.py`, `mesh_pairing_routes.py`, `mesh/inbox.py`, `store_schema.py`, `settings_validation.py`, `semantic_clustering.py`, `topic_attention_analysis.py`, `memory/graph.py`) were materially reduced by extraction into facade + helper modules
- `POST /chat` and `GET /chat/context` now share the same runtime-context path via `chat_route_support.session_payload`
- Goals-, Chat- und Shell-CSS wurden in importierte Slices getrennt, statt große Einzeldateien weiter anwachsen zu lassen
- maintainability pressure now concentrates more in `python/eidolon/web/index.html`, `python/eidolon/web/app-shell.js`, `python/agent_server.py`, `python/eidolon/core/mesh_service.py`, and `python/eidolon/user/topic_attention.py`

### Verdict
**Functionally improved, maintainability materially better, and the shared chat/operate context path is now unified at the route layer.**

## Priority order
1. Keep a single canonical doc hierarchy
2. Continue shrinking the remaining large UI/app integration hotspots (`python/eidolon/web/index.html`, `python/eidolon/web/app-shell.js`, `python/agent_server.py`)
3. Continue splitting remaining domain hotspots by product boundary, especially `python/eidolon/core/mesh_service.py`, `python/eidolon/core/auth_entities.py`, and `python/eidolon/user/topic_attention.py`
4. Keep superseded findings and historical docs explicitly marked so archive material cannot masquerade as current truth
