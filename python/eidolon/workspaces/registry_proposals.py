from __future__ import annotations

from datetime import datetime, timezone

from eidolon.workspaces.contracts import build_workspace_semantic_frame, map_workspace_state_to_product_state
from eidolon.workspaces.message_candidate import is_preserved_workspace


def propose_from_topics(registry) -> dict:
    data = registry.snapshot()
    if not registry.feature_enabled():
        return data
    topics = registry.topics.snapshot().get('topics', [])
    user = registry.user_model.get()
    previous = {w['workspace_id']: w for w in data.get('workspaces', [])}
    proposed = []
    for topic in topics[:5]:
        contract = registry.generator.propose(topic, user).to_dict()
        prior = previous.get(contract['workspace_id'], {})
        runtime_state = prior.get('state', 'suggested')
        metadata = {**(contract.get('metadata') or {}), **(prior.get('metadata') or {})}
        topic_signals = {**topic, **metadata}
        contract.update({
            'state': runtime_state,
            'metadata': metadata,
            'product_state': map_workspace_state_to_product_state(runtime_state, topic_signals),
            'health': 'ok',
            'last_updated': datetime.now(timezone.utc).isoformat(),
        })
        proposed.append(contract)
    enriched = []
    topic_map = {topic.get('topic_id'): topic for topic in topics}
    for workspace in proposed:
        state = registry.state_store.ensure_workspace_state(workspace)
        topic = topic_map.get((workspace.get('metadata') or {}).get('topic_id'))
        orchestration = registry.orchestrator.evaluate(workspace | {'state_data': state}, topic)
        semantic_frame = build_workspace_semantic_frame(workspace, state | {'orchestration': orchestration})
        state = registry.state_store.update_state(workspace['workspace_id'], {'orchestration': orchestration, 'semantic_frame': semantic_frame, 'product_state': semantic_frame['active_context']})
        workspace['state_data'] = state
        workspace['product_state'] = state.get('product_state', workspace.get('product_state'))
        workspace['semantic_frame'] = state.get('semantic_frame', {})
        enriched.append(workspace)
    claimed = {workspace.get('workspace_id') for workspace in enriched}
    for workspace_id, prior in previous.items():
        if workspace_id in claimed or not is_preserved_workspace(prior):
            continue
        state = registry.state_store.ensure_workspace_state(prior)
        prior = {**prior, 'state_data': state, 'product_state': prior.get('product_state') or state.get('product_state')}
        enriched.append(prior)
        claimed.add(workspace_id)
    suggestions = registry.proactive_store.generate(topics, enriched, user)
    payload = {'workspaces': enriched, 'feature_flags': data.get('feature_flags', {'workspace_adaptive_modules': True}), 'proactive_assistance': suggestions, 'context_model': registry.build_context_model(enriched)}
    registry._save({'workspaces': enriched, 'feature_flags': payload['feature_flags']})
    return payload
