from __future__ import annotations

from typing import Any

from eidolon.workspaces.workspace_payload_assistance import merge_proactive_assistance
from eidolon.workspaces.workspace_payload_context import build_workspace_work_context, sync_workspace_operate
from eidolon.workspaces.workspace_payload_records import project_backed_workspaces, project_to_workspace_record
from eidolon.workspaces.workspace_payload_views import overview_user_payload


def merged_workspace_payload(project_service, registry) -> dict[str, Any]:
    topic_payload = registry.propose_from_topics()
    topic_workspaces = list(topic_payload.get('workspaces', []))
    project_workspaces = project_backed_workspaces(project_service, registry)
    project_ids = {workspace.get('workspace_id') for workspace in project_workspaces}
    merged = project_workspaces + [workspace for workspace in topic_workspaces if workspace.get('workspace_id') not in project_ids]
    return {
        'workspaces': merged,
        'proactive_assistance': merge_proactive_assistance(project_workspaces, topic_payload, merged),
        'context_model': registry.build_context_model(merged),
        'topics': registry.topics.snapshot().get('topics', [])[:5],
    }


def unified_work_context(registry, operate_service, data: dict[str, Any], *, message: str = '', session: dict[str, Any] | None = None, source: str = 'workspace') -> dict[str, Any]:
    return build_workspace_work_context(registry, operate_service, data, message=message, session=session, source=source)


def overview_payload(registry, operate_service, data: dict[str, Any]) -> dict[str, Any]:
    operate_snapshot = sync_workspace_operate(operate_service, data)
    workspaces = data.get('workspaces', [])
    suggestions = data.get('proactive_assistance', {})
    user = registry.user_model.get()
    suggestion_list = suggestions.get('suggestions', []) if isinstance(suggestions, dict) else []
    return {
        'user': overview_user_payload(user),
        'topics': data.get('topics', []),
        'workspaces': workspaces,
        'proactive_assistance': suggestion_list[:3],
        'context_model': data.get('context_model', {}),
        'feature_enabled': registry.feature_enabled(),
        'total': len(workspaces),
        'operate': operate_snapshot,
        'work_kernel': build_workspace_work_context(registry, operate_service, data, source='workspace', operate_snapshot=operate_snapshot),
    }


def workspace_detail_payload(project_service, registry, operate_service, workspace_id: str) -> dict[str, Any] | None:
    data = merged_workspace_payload(project_service, registry)
    for workspace in data.get('workspaces', []):
        if workspace.get('workspace_id') != workspace_id:
            continue
        payload = dict(workspace)
        operate_snapshot = sync_workspace_operate(operate_service, {'workspaces': [payload]})
        payload['operate'] = operate_snapshot
        payload['work_kernel'] = build_workspace_work_context(registry, operate_service, data, source='workspace_detail', operate_snapshot=operate_snapshot)
        return payload
    return None
