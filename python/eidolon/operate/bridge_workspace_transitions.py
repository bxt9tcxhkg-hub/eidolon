from __future__ import annotations

from typing import Any

from eidolon.operate.service import OperateService


def derive_decomposition_mode(summary: dict[str, Any], next_actions: list[str]) -> str:
    signals = int(summary.get('blocked', 0)) + int(summary.get('in_progress', 0)) + len(next_actions)
    return 'multi_stream' if signals >= 2 else 'single_stream'


def align_run_state_from_summary(service: OperateService, run_id: str, summary: dict[str, Any]) -> Any:
    run = service.get_run(run_id)
    if run is None:
        return None
    blocked = int(summary.get('blocked', 0) or 0)
    in_progress = int(summary.get('in_progress', 0) or 0)
    ready = int(summary.get('ready', 0) or 0)
    done = int(summary.get('done', 0) or 0)
    total = int(summary.get('total', 0) or 0)
    desired = None
    if blocked > 0 and in_progress == 0:
        desired = 'blocked'; reason = 'Workspace has open blockers'; phase = run.current_phase or 'plan'; next_transition = None
    elif in_progress > 0:
        desired = 'acting'; reason = 'Workspace has active in-progress work'; phase = 'execute'; next_transition = 'verify'
    elif total > 0 and done == total:
        desired = 'verifying'; reason = 'All workspace items are complete; verification required'; phase = 'verify'; next_transition = 'complete'
    elif ready > 0:
        desired = 'planning'; reason = 'Workspace has ready work with no active execution'; phase = 'plan'; next_transition = 'execute'
    if not desired or desired == run.state:
        return run
    try:
        if run.state == 'understanding' and desired != 'planning':
            run = service.set_run_state(run_id, 'planning', 'Workspace bootstrap planning established', current_phase='plan', next_transition='execute')
        if desired == 'acting' and run.state == 'planning':
            return service.set_run_state(run_id, 'acting', reason, current_phase=phase, next_transition=next_transition)
        if desired == 'blocked' and run.state in {'understanding', 'planning', 'acting', 'waiting'}:
            return service.set_run_state(run_id, 'blocked', reason, current_phase=phase, next_transition=next_transition)
        if desired == 'planning' and run.state in {'understanding', 'blocked', 'waiting'}:
            return service.set_run_state(run_id, 'planning', reason, current_phase=phase, next_transition=next_transition)
        if desired == 'verifying' and run.state == 'acting':
            return service.set_run_state(run_id, 'verifying', reason, current_phase=phase, next_transition=next_transition)
    except ValueError:
        return service.get_run(run_id)
    return service.get_run(run_id)
