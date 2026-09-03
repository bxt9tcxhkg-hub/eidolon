from __future__ import annotations

from eidolon.core.autonomy_models import TERMINAL_STATES, Step
from eidolon.core.autonomy_store import now_iso


def revalidate(engine, deriver, health: dict, auto_close: bool = False) -> dict:
    results: list[dict] = []
    now = now_iso()
    for goal in list(engine.store.goals.values()):
        if not goal.problem_key:
            continue
        verdict = deriver.verify(goal.problem_key, health)
        goal.verified_at = now
        if not verdict['checkable']:
            goal.verify_state = 'unverifiable'
        elif verdict['still_open']:
            goal.verify_state = 'open'
            goal.evidence = verdict['evidence']
        else:
            goal.verify_state = 'resolved'
            goal.evidence = verdict['evidence']
        entry = {
            'id': goal.id,
            'title': goal.title,
            'problem_key': goal.problem_key,
            'status': goal.status,
            'verify_state': goal.verify_state,
            'evidence': verdict['evidence'],
            'auto_closed': False,
        }
        if auto_close and goal.verify_state == 'resolved' and goal.status not in TERMINAL_STATES:
            old_status = goal.status
            goal.status = 'done'
            goal.completed_at = now
            goal.progress = 1.0
            for step in goal.steps:
                if isinstance(step, Step):
                    step.done = True
                    step.completed_at = step.completed_at or now
            goal.last_error = None
            engine.store.add_log(goal.id, 'auto_closed', f"{old_status} → done; Problem behoben: {verdict['evidence'][:90]}")
            entry['status'] = goal.status
            entry['auto_closed'] = True
        if goal.verify_state == 'open' and goal.status == 'done':
            entry['regression'] = True
            engine.store.add_log(goal.id, 'regression_detected', verdict['evidence'][:110])
        results.append(entry)
    engine.store.save()
    return {
        'ok': True,
        'checked': len(results),
        'resolved': sum(1 for row in results if row['verify_state'] == 'resolved'),
        'still_open': sum(1 for row in results if row['verify_state'] == 'open'),
        'unverifiable': sum(1 for row in results if row['verify_state'] == 'unverifiable'),
        'auto_closed': sum(1 for row in results if row['auto_closed']),
        'regressions': [row for row in results if row.get('regression')],
        'results': results,
    }
