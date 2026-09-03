from __future__ import annotations

from pathlib import Path
from typing import Any
import hashlib

from eidolon.workspaces.contracts import WorkspaceModuleContract

MODULE_LIBRARY = {
    'planner_workspace': ['next_actions', 'timeline', 'dependencies', 'notes'],
    'tracker_workspace': ['status_tracker', 'progress_log', 'next_actions', 'notes'],
    'decision_workspace': ['decision_matrix', 'criteria_list', 'options_board', 'notes'],
    'knowledge_workspace': ['question_list', 'knowledge_map', 'notes', 'insights'],
    'project_workspace': ['board', 'graph', 'dependencies', 'next_actions', 'details'],
    'review_workspace': ['journal', 'patterns', 'reflection', 'next_actions'],
    'mixed_workspace': ['overview', 'next_actions', 'notes', 'details'],
}


class WorkspaceGenerator:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)

    def classify_needs(self, topic: dict[str, Any], user_model: dict[str, Any]) -> dict[str, float]:
        needs = dict(topic.get('needs') or {})
        if user_model.get('prefers_visual_planning'):
            needs['planning'] = round(float(needs.get('planning', 0.0)) + 0.15, 3)
        if user_model.get('likes_dependency_visibility'):
            needs['execution'] = round(float(needs.get('execution', 0.0)) + 0.1, 3)
        return needs

    def choose_layout(self, needs: dict[str, float], user_model: dict[str, Any]) -> tuple[str, str]:
        top = sorted(needs.items(), key=lambda kv: kv[1], reverse=True)
        dominant = top[0][0] if top and top[0][1] > 0 else 'knowledge'
        if user_model.get('preferred_project_view') == 'hybrid' and dominant in {'planning', 'execution', 'tracking'}:
            return 'hybrid', 'project_workspace'
        mapping = {
            'planning': ('planner', 'planner_workspace'),
            'tracking': ('tracker', 'tracker_workspace'),
            'decision': ('decision', 'decision_workspace'),
            'knowledge': ('knowledge', 'knowledge_workspace'),
            'execution': ('board', 'project_workspace'),
            'reflection': ('review', 'review_workspace'),
        }
        return mapping.get(dominant, ('hybrid', 'mixed_workspace'))

    def propose(self, topic: dict[str, Any], user_model: dict[str, Any]) -> WorkspaceModuleContract:
        label = str(topic.get('label') or 'Workspace')
        needs = self.classify_needs(topic, user_model)
        layout, workspace_type = self.choose_layout(needs, user_model)
        modules = MODULE_LIBRARY.get(workspace_type, MODULE_LIBRARY['mixed_workspace'])
        token = hashlib.sha1(f"{label}:{workspace_type}".encode('utf-8')).hexdigest()[:10]
        return WorkspaceModuleContract(
            workspace_id=f'ws_{token}',
            topic_label=label,
            workspace_type=workspace_type,
            layout_template=layout,
            modules=modules,
            metadata={
                'needs': needs,
                'topic_id': topic.get('topic_id'),
                'workspace_suggestion': topic.get('workspace_suggestion'),
                'entities': topic.get('entities', []),
            },
        )
