from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))

from eidolon.chat_runtime import build_grounded_fallback_reply  # type: ignore[import-not-found]
from eidolon.domain.mission.product_phases import (  # type: ignore[import-not-found]
    PRODUCT_WORKFLOW_PHASES,
    build_phase_preservation_payload,
)
from eidolon.domain.mission.state_machine import advance_run_state  # type: ignore[import-not-found]
from eidolon.operate.bridge import build_operate_snapshot  # type: ignore[import-not-found]
from eidolon.operate.service import OperateService  # type: ignore[import-not-found]
from eidolon.core.evidence import EvidenceStore  # type: ignore[import-not-found]


def _temp_service(tmp_path):
    evidence_db = tmp_path / 'evidence.db'
    legacy_store = EvidenceStore(evidence_db)
    return OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=legacy_store)


def test_advance_run_state_uses_canonical_transitions():
    planning = advance_run_state('planning')
    acting = advance_run_state('acting')
    verifying = advance_run_state('verifying')

    assert planning['new_state'] == 'spawning_work'
    assert planning['current_phase'] == 'execute'
    assert planning['next_transition'] == 'execute'

    assert acting['new_state'] == 'verifying'
    assert acting['current_phase'] == 'verify'
    assert acting['next_transition'] == 'finalize'

    assert verifying['new_state'] == 'completed'
    assert verifying['current_phase'] == 'finalize'
    assert verifying['next_transition'] is None
    assert verifying['result_status'] == 'success'


def test_build_operate_snapshot_exposes_canonical_run_and_active_pods(tmp_path):
    service = _temp_service(tmp_path)
    started = service.start_objective(
        user_request='verify release train',
        title='Verify release train',
        normalized_goal='Verify release train end to end',
        scope_summary='verify release train',
        decomposition_mode='multi_stream',
    )
    run = started['run']
    subagent = service.spawn_subagent_run(
        run_id=run.id,
        display_name='Verification Stream',
        function_type='verifier',
        mission='Run regression verification',
        state_reason='Verification worker created',
    )
    service.set_subagent_state(subagent.id, 'running', 'Verification in progress')
    service.emit_evidence(
        owner_type='subagent',
        owner_id=subagent.id,
        kind='workspace_mutation',
        title='workspace mutation',
        summary='Observed workspace change',
    )

    snapshot = build_operate_snapshot(service, run.id)

    assert snapshot['run']['canonical_phase'] == 'understand'
    assert snapshot['run']['canonical_next_transition'] == 'plan'
    assert snapshot['run']['phase_preservation']['workflow_phases'][-1] == 'verification_and_return'
    assert snapshot['run']['phase_preservation']['phase_status']['understand_and_structure']['preserved'] is True
    assert len(snapshot['active_pods']) == 1
    assert snapshot['active_pods'][0]['id'] == subagent.id
    assert snapshot['subagents'][0]['function_family'] == 'verifier'
    assert snapshot['evidence'][0]['evidence_status'] == 'observed'


def test_grounded_fallback_reply_stays_honestly_empty_without_real_context():
    reply = build_grounded_fallback_reply({
        'user_intent': {'classification': 'unknown'},
        'workflow_state': {'current_context_state': 'no_live_context', 'next_step': None},
        'project_context': {},
        'workspace_context': {'visible_suggestions': []},
    })

    assert 'keinen belastbaren Projekt-, Pod- oder Evidenzzustand' in reply
    assert 'Konkreter nächster Schritt: Formuliere ein Ziel' in reply


def test_phase_preservation_payload_covers_all_product_workflow_phases():
    assert PRODUCT_WORKFLOW_PHASES == (
        'chat_entry',
        'understand_and_structure',
        'context_classification',
        'project_formation',
        'workspace_composition',
        'responsibility_derivation',
        'execution',
        'verification_and_return',
    )

    payload = build_phase_preservation_payload(
        run_state='planning',
        current_phase='plan',
        context_state='project_candidate',
        has_objective=True,
        current_view='operate',
        has_subagents=False,
        has_blocker=False,
        has_approval=False,
        result_status=None,
    )

    assert payload['missing_phases'] == []
    assert payload['phase_status']['chat_entry']['preserved'] is True
    assert payload['phase_status']['understand_and_structure']['preserved'] is True
    assert payload['phase_status']['context_classification']['preserved'] is True
    assert payload['phase_status']['project_formation']['preserved'] is True
    assert payload['phase_status']['workspace_composition']['preserved'] is True
    assert payload['phase_status']['responsibility_derivation']['preserved'] is False
    assert payload['phase_status']['execution']['preserved'] is False
    assert payload['phase_status']['verification_and_return']['preserved'] is False


def test_phase_preservation_payload_marks_complete_execution_path_as_fully_preserved():
    payload = build_phase_preservation_payload(
        run_state='completed',
        current_phase='finalize',
        context_state='active_project',
        has_objective=True,
        current_view='operate',
        has_subagents=True,
        has_blocker=False,
        has_approval=False,
        result_status='success',
    )

    assert payload['missing_phases'] == []
    assert all(item['preserved'] for item in payload['phase_status'].values())
