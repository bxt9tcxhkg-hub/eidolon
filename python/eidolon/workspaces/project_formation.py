from __future__ import annotations

from typing import Any

FORMATION_STATES = ('no_live_context', 'chat_topic', 'project_candidate', 'active_project')
ALLOWED_TRANSITIONS = {
    'no_live_context': frozenset({'chat_topic'}),
    'chat_topic': frozenset({'project_candidate'}),
    'project_candidate': frozenset({'active_project', 'chat_topic'}),
    'active_project': frozenset({'project_candidate'}),
}
CONFIRMATION_REQUIRED = frozenset({('project_candidate', 'active_project')})
DURABLE_PROJECT_TRANSITIONS = frozenset({('project_candidate', 'active_project')})


class FormationError(ValueError):
    pass


def _signal_score(topic: dict[str, Any] | None) -> tuple[float, float]:
    topic = topic or {}
    return float(topic.get('action_relevance', 0) or 0), float(topic.get('recurrence_score', 0) or 0)


def has_candidate_signals(topic: dict[str, Any] | None) -> bool:
    action, recurrence = _signal_score(topic)
    return action >= 0.45 or recurrence >= 0.3


def is_formation_confirmed(source: dict[str, Any] | None) -> bool:
    source = source or {}
    if source.get('formation_confirmed') is True:
        return True
    if str(source.get('formation_source') or '') in {'user_created_project', 'user_confirmed_promotion'}:
        return True
    return False


def propose_product_state(runtime_state: str | None, topic: dict[str, Any] | None = None, *, confirmed: bool | None = None, stored_product_state: str | None = None) -> str:
    topic = topic or {}
    confirmed = is_formation_confirmed(topic) if confirmed is None else bool(confirmed)
    stored = stored_product_state or topic.get('stored_product_state') or topic.get('product_state')
    if stored == 'active_project' and confirmed:
        return 'active_project'
    if confirmed and str(runtime_state or '') == 'active':
        return 'active_project'
    if has_candidate_signals(topic) or str(runtime_state or '') == 'active':
        return 'project_candidate'
    if str(runtime_state or 'suggested') in {'suggested', 'prepared', 'suspended', 'archived', 'chat_topic', ''}:
        return 'chat_topic'
    return 'chat_topic'


def map_workspace_state_to_product_state(runtime_state: str | None, topic: dict[str, Any] | None = None) -> str:
    return propose_product_state(runtime_state, topic)


def transition_allowed(from_state: str, to_state: str) -> bool:
    return to_state in ALLOWED_TRANSITIONS.get(from_state, frozenset())


def requires_confirmation(from_state: str, to_state: str) -> bool:
    return (from_state, to_state) in CONFIRMATION_REQUIRED


def creates_durable_project(from_state: str, to_state: str) -> bool:
    return (from_state, to_state) in DURABLE_PROJECT_TRANSITIONS


def apply_transition(from_state: str, to_state: str, *, confirmed: bool = False, reason: str = '') -> dict[str, Any]:
    if from_state not in FORMATION_STATES or to_state not in FORMATION_STATES:
        raise FormationError(f'Unbekannter Formationszustand: {from_state} → {to_state}')
    if from_state == to_state:
        return {'ok': True, 'from_state': from_state, 'to_state': to_state, 'changed': False, 'reason': reason or 'noop'}
    if not transition_allowed(from_state, to_state):
        raise FormationError(f'Übergang {from_state} → {to_state} ist nicht erlaubt')
    if requires_confirmation(from_state, to_state) and not confirmed:
        raise FormationError('Übergang nach active_project braucht sichtbare Bestätigung (confirmed=true); stille dauerhafte Projekt-Bots sind nicht erlaubt')
    return {
        'ok': True,
        'from_state': from_state,
        'to_state': to_state,
        'changed': True,
        'reason': reason or ('user_confirmed_promotion' if confirmed else 'visible_proactive_formation'),
        'requires_confirmation': False,
        'creates_durable_project': creates_durable_project(from_state, to_state),
        'formation_confirmed': confirmed or not requires_confirmation(from_state, to_state),
        'formation_source': 'user_confirmed_promotion' if creates_durable_project(from_state, to_state) else 'visible_proactive_formation',
    }
