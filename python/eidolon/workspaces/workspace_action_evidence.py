from __future__ import annotations

from eidolon.core.evidence import get_evidence_store
from eidolon.operate.bridge import record_workspace_action


def record_workspace_evidence(*, operate_service, workspace, workspace_id: str, module_id: str, action: str, clean_payload: dict, changed: bool, before_summary: dict, after_summary: dict | None, element_id: str | None, selection_reason: str, selection_score):
    evidence = get_evidence_store()
    action_id = evidence.log_action(command=f'workspace:{workspace_id}:{module_id}:{action}', exit_code=0 if changed else 1, stdout=str({'payload': clean_payload, 'result_element_id': element_id, 'selection_reason': selection_reason, 'selection_score': selection_score}), stderr=None if changed else 'workspace action produced no mutation')
    evidence.log_observation(action_id, kind='workspace_mutation', description=f'{module_id}.{action} on {workspace_id}', detail=str({'before': before_summary, 'after': after_summary, 'payload': clean_payload, 'selection_reason': selection_reason, 'selection_score': selection_score}))
    claim = f'Workspace {workspace_id} changed via {module_id}.{action}'
    verification_status = 'verified' if changed else 'blocked'
    evidence.log_verification(action_id, claim=claim, status=verification_status, evidence=str({'before': before_summary, 'after': after_summary, 'element_id': element_id, 'selection_reason': selection_reason, 'selection_score': selection_score}))
    if not changed:
        evidence.log_blocked(claim=claim, reason=selection_reason or 'workspace action produced no mutation', capability=f'workspace:{module_id}.{action}')
    operate = record_workspace_action(operate_service, {'workspaces': [workspace]} if workspace else None, workspace_id=workspace_id, module_id=module_id, action=action, mutation_payload=clean_payload, changed=bool(changed), before_summary=before_summary, after_summary=after_summary, element_id=element_id, selection_reason=selection_reason)
    return {'action_id': action_id, 'claim': claim, 'status': verification_status}, operate
