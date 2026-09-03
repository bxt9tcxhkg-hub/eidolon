from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))

from eidolon.core import config
from eidolon.operate.contracts import (  # type: ignore[import-not-found]
    AgentRunRecord,
    AgentRunState,
    EvidenceItemRecord,
    NextActionKind,
    ObjectiveRecord,
    SubAgentRunRecord,
    SubAgentRunState,
    TransitionEventRecord,
    WorkSessionRecord,
    is_valid_run_transition,
    is_valid_subagent_transition,
)
from eidolon.operate.store import OperateStore  # type: ignore[import-not-found]


def test_operate_config_exposes_storage_paths():
    assert config.OPERATE_DIR.name == 'operate'
    assert config.OPERATE_DB.name == 'operate.db'
    assert config.OPERATE_EVENTS_FILE.name == 'events.jsonl'


def test_operate_contract_records_can_be_constructed_with_canonical_states():
    session = WorkSessionRecord(
        id='ws_1',
        title='Fix deployment timeout',
        status='active',
        current_run_id='run_1',
        current_objective_id='obj_1',
        current_view='operate',
        source_kind='chat',
        created_at='2026-08-28T09:00:00Z',
        updated_at='2026-08-28T09:00:00Z',
        context_kind='project_candidate',
        entry_message_id='msg_123',
        linked_workspace_id='proj_1',
        surface_reason='user_selected_project',
    )
    objective = ObjectiveRecord(
        id='obj_1',
        session_id='ws_1',
        title='Fix deployment timeout',
        user_request='fix deployment timeout',
        normalized_goal='Diagnose and resolve deployment timeout',
        scope_summary='diagnosis, fix, verification',
        decomposition_mode='multi_stream',
        status='active',
        created_at='2026-08-28T09:00:00Z',
        updated_at='2026-08-28T09:00:00Z',
        candidate_source='chat_clarification',
        acceptance_state='accepted',
        goal_confidence=0.85,
        clarification_completeness=0.7,
        linked_project_id='proj_1',
    )
    run = AgentRunRecord(
        id='run_1',
        session_id='ws_1',
        objective_id='obj_1',
        state='understanding',
        state_reason='New objective created',
        current_phase='understand',
        next_transition='plan',
        autonomy_mode='bounded_autonomous',
        approval_required=False,
        blocking_issue_id=None,
        interruptible=True,
        pending_interrupt_count=0,
        last_interrupt_at=None,
        result_status=None,
        started_at='2026-08-28T09:00:00Z',
        updated_at='2026-08-28T09:00:00Z',
        ended_at=None,
        product_phase='understand_and_structure',
        phase_provenance='runtime_mapping',
        current_owner='eidolon',
    )
    subagent = SubAgentRunRecord(
        id='sa_1',
        parent_run_id='run_1',
        objective_id='obj_1',
        display_name='Verification',
        function_type='verifier',
        mission='Run regression verification',
        state='queued',
        state_reason='Spawned for verification',
        assigned_by='system',
        blocking_issue_id=None,
        evidence_count=0,
        output_count=0,
        result_status=None,
        started_at=None,
        updated_at='2026-08-28T09:00:00Z',
        ended_at=None,
    )
    evidence = EvidenceItemRecord(
        id='ev_1',
        owner_type='run',
        owner_id='run_1',
        kind='test_result',
        title='Regression suite',
        summary='18 passed',
        artifact_ref='file:///tmp/report.xml',
        metadata_json={'passed': 18},
        created_at='2026-08-28T09:00:00Z',
    )
    event = TransitionEventRecord(
        id='tr_1',
        actor_type='run',
        actor_id='run_1',
        transition_type='state_change',
        from_state='understanding',
        to_state='planning',
        summary='Moved into planning',
        evidence_ids=['ev_1'],
        created_at='2026-08-28T09:00:01Z',
    )

    assert session.current_view == 'operate'
    assert objective.decomposition_mode == 'multi_stream'
    assert run.state == 'understanding'
    assert subagent.state == 'queued'
    assert evidence.kind == 'test_result'
    assert event.to_state == 'planning'
    assert 'verifying' in AgentRunState.__args__
    assert 'queued' in SubAgentRunState.__args__
    assert 'next_step' in NextActionKind.__args__
    assert session.context_kind == 'project_candidate'
    assert session.entry_message_id == 'msg_123'
    assert session.linked_workspace_id == 'proj_1'
    assert session.surface_reason == 'user_selected_project'
    assert objective.candidate_source == 'chat_clarification'
    assert objective.acceptance_state == 'accepted'
    assert objective.goal_confidence == 0.85
    assert objective.clarification_completeness == 0.7
    assert objective.linked_project_id == 'proj_1'
    assert run.product_phase == 'understand_and_structure'
    assert run.phase_provenance == 'runtime_mapping'
    assert run.current_owner == 'eidolon'


def test_operate_session_continuity_across_context_transitions(tmp_path):
    db_path = tmp_path / 'operate.db'
    store = OperateStore(db_path)
    session = store.create_session(
        title='Fix deployment timeout',
        source_kind='chat',
        current_view='operate',
        context_kind='chat_topic',
        entry_message_id='msg_1',
    )
    objective = store.create_objective(
        session_id=session.id,
        title='Fix deployment timeout',
        user_request='fix deployment timeout',
        normalized_goal='Diagnose and resolve deployment timeout',
        scope_summary='diagnosis, fix, verification',
        decomposition_mode='multi_stream',
        candidate_source='chat_clarification',
        acceptance_state='accepted',
        goal_confidence=0.85,
        clarification_completeness=0.7,
        linked_project_id='proj_1',
    )
    run = store.create_agent_run(
        session_id=session.id,
        objective_id=objective.id,
        state='understanding',
        state_reason='New objective created',
        current_phase='understand',
        next_transition='plan',
        autonomy_mode='bounded_autonomous',
    )
    session = store.update_session(session.id, current_run_id=run.id, current_objective_id=objective.id, context_kind='project_candidate', linked_workspace_id='proj_1', surface_reason='user_selected_project')
    assert session.context_kind == 'project_candidate'
    assert session.linked_workspace_id == 'proj_1'
    assert session.surface_reason == 'user_selected_project'
    assert session.current_run_id == run.id
    assert session.current_objective_id == objective.id
    session = store.update_session(session.id, context_kind='active_project')
    assert session.context_kind == 'active_project'
    assert session.current_run_id == run.id
    assert session.current_objective_id == objective.id


def test_operate_run_phase_mapping_and_interrupt_classification(tmp_path):
    from eidolon.domain.mission.state_machine import product_phase_for_state
    from eidolon.operate.service import OperateService
    from eidolon.core.evidence import EvidenceStore

    service = OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=EvidenceStore(tmp_path / 'evidence.db'))
    started = service.start_objective(user_request='Ship the operate kernel', decomposition_mode='multi_stream')
    run = started['run']

    assert run.product_phase == 'understand_and_structure'
    assert product_phase_for_state('understanding') == 'understand_and_structure'
    assert product_phase_for_state('planning') == 'understand_and_structure'
    assert product_phase_for_state('acting') == 'execution'
    assert product_phase_for_state('verifying') == 'verification_and_return'
    assert product_phase_for_state('completed') == 'verification_and_return'

    service.advance_run(run.id, reason='Moving to planning')
    run = service.get_run(run.id)
    assert run.product_phase == 'understand_and_structure'
    assert run.current_owner == 'eidolon'

    interrupted = service.interrupt_run(run.id, 'refine', 'User wants to refine')
    assert interrupted.interrupt_classification == 'refine'
    assert interrupted.state == 'planning'
    assert interrupted.pending_interrupt_count == 1

    service.advance_run(run.id, reason='Moving to spawning work')
    run = service.get_run(run.id)
    assert run.product_phase == 'execution'

    service.advance_run(run.id, reason='Moving to acting')
    run = service.get_run(run.id)
    assert run.product_phase == 'execution'

    service.advance_run(run.id, reason='Moving to verifying')
    run = service.get_run(run.id)
    assert run.product_phase == 'verification_and_return'

    service.advance_run(run.id, reason='Moving to completed')
    run = service.get_run(run.id)
    assert run.product_phase == 'verification_and_return'
    assert run.completion_summary == 'Moving to completed'
    assert run.state == 'completed'


def test_operate_run_phase_continuity_after_blocker_and_approval(tmp_path):
    from eidolon.operate.service import OperateService
    from eidolon.core.evidence import EvidenceStore

    service = OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=EvidenceStore(tmp_path / 'evidence.db'))
    started = service.start_objective(user_request='Ship the operate kernel', decomposition_mode='multi_stream')
    run = started['run']

    service.advance_run(run.id, reason='Moving to planning')
    service.advance_run(run.id, reason='Moving to spawning work')
    service.advance_run(run.id, reason='Moving to acting')

    blocker, _ = service.open_blocking_issue(run.id, 'Need input', 'Waiting for user input', resolution_hint='Please clarify')
    run = service.get_run(run.id)
    assert run.state == 'blocked'
    assert run.product_phase == 'understand_and_structure'

    service.resolve_blocking_issue(blocker.id, resume_state='planning', state_reason='User clarified')
    run = service.get_run(run.id)
    assert run.state == 'planning'
    assert run.product_phase == 'understand_and_structure'
    assert run.session_id == started['session'].id
    assert run.objective_id == started['objective'].id

    service.advance_run(run.id, reason='Moving to spawning work')
    service.advance_run(run.id, reason='Moving to acting')
    service.advance_run(run.id, reason='Moving to verifying')

    gate = service.request_approval(run.id, 'Deploy?', 'Need explicit approval before deploy', 'release')
    run = service.get_run(run.id)
    assert run.state == 'waiting'
    assert run.product_phase == 'understand_and_structure'

    service.resolve_approval(gate.id, decision='approved', resolved_by='user')
    run = service.get_run(run.id)
    assert run.state == 'planning'
    assert run.product_phase == 'understand_and_structure'

    service.advance_run(run.id, reason='Moving to spawning work')
    service.advance_run(run.id, reason='Moving to acting')
    service.advance_run(run.id, reason='Moving to verifying')
    service.advance_run(run.id, reason='Moving to completed')

    run = service.get_run(run.id)
    assert run.state == 'completed'
    assert run.product_phase == 'verification_and_return'
    assert run.completion_summary == 'Moving to completed'
    assert run.session_id == started['session'].id
    assert run.objective_id == started['objective'].id


def test_operate_specialist_subagent_controlled_vocabulary_and_anti_overclaim(tmp_path):
    from eidolon.operate.contract_types import (
        SPECIALIST_FAMILIES,
        SubAgentFunctionType,
        is_generic_execution_record,
        is_specialist_family,
    )
    from eidolon.operate.service import OperateService
    from eidolon.core.evidence import EvidenceStore

    assert 'planner' in SPECIALIST_FAMILIES
    assert 'research' in SPECIALIST_FAMILIES
    assert 'builder' in SPECIALIST_FAMILIES
    assert 'verifier' in SPECIALIST_FAMILIES
    assert 'resolver' in SPECIALIST_FAMILIES
    assert 'operator' in SPECIALIST_FAMILIES
    assert 'monitor' in SPECIALIST_FAMILIES
    assert 'reconciler' in SPECIALIST_FAMILIES

    assert 'planner' in SubAgentFunctionType.__args__
    assert 'research' in SubAgentFunctionType.__args__
    assert 'builder' in SubAgentFunctionType.__args__
    assert 'verifier' in SubAgentFunctionType.__args__
    assert 'resolver' in SubAgentFunctionType.__args__
    assert 'operator' in SubAgentFunctionType.__args__
    assert 'monitor' in SubAgentFunctionType.__args__
    assert 'reconciler' in SubAgentFunctionType.__args__
    assert 'executor' in SubAgentFunctionType.__args__

    assert is_specialist_family('planner') is True
    assert is_specialist_family('verifier') is True
    assert is_specialist_family('research') is True
    assert is_specialist_family('executor') is False
    assert is_generic_execution_record('executor') is True
    assert is_generic_execution_record('planner') is False
    assert is_generic_execution_record(None) is False
    assert is_specialist_family(None) is False

    service = OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=EvidenceStore(tmp_path / 'evidence.db'))
    started = service.start_objective(user_request='Ship the operate kernel', decomposition_mode='multi_stream')
    run = started['run']

    specialist = service.spawn_subagent_run(
        run_id=run.id,
        display_name='Plan the work',
        function_type='planner',
        mission='Plan the next phase of work',
        state_reason='User requested planning',
    )
    assert specialist.function_type == 'planner'
    assert is_specialist_family(specialist.function_type) is True

    verifier = service.spawn_subagent_run(
        run_id=run.id,
        display_name='Verify the work',
        function_type='verifier',
        mission='Verify the completed work',
        state_reason='User requested verification',
    )
    assert verifier.function_type == 'verifier'
    assert is_specialist_family(verifier.function_type) is True

    generic = service.spawn_subagent_run(
        run_id=run.id,
        display_name='Do the work',
        function_type='executor',
        mission='Execute the planned work',
        state_reason='User requested execution',
    )
    assert generic.function_type == 'executor'
    assert is_specialist_family(generic.function_type) is False
    assert is_generic_execution_record(generic.function_type) is True

    all_subagents = service.list_subagent_runs(run.id)
    assert len(all_subagents) == 3

    specialists = [s for s in all_subagents if is_specialist_family(s.function_type)]
    generics = [s for s in all_subagents if is_generic_execution_record(s.function_type)]
    assert len(specialists) == 2
    assert len(generics) == 1


def test_operate_product_surface_does_not_overclaim_specialization(tmp_path):
    from eidolon.operate.contract_types import is_specialist_family, is_generic_execution_record
    from eidolon.operate.service import OperateService
    from eidolon.core.evidence import EvidenceStore

    service = OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=EvidenceStore(tmp_path / 'evidence.db'))
    started = service.start_objective(user_request='Ship the operate kernel', decomposition_mode='multi_stream')
    run = started['run']

    service.spawn_subagent_run(
        run_id=run.id,
        display_name='Do generic work',
        function_type='executor',
        mission='Execute some work',
        state_reason='User requested execution',
    )

    subagents = service.list_subagent_runs(run.id)
    assert len(subagents) == 1
    assert is_specialist_family(subagents[0].function_type) is False
    assert is_generic_execution_record(subagents[0].function_type) is True


def test_operate_evidence_record_severity_and_completion_grade_fields():
    from eidolon.operate.contract_evidence_records import EvidenceItemRecord
    from eidolon.operate.contract_types import EvidenceKind, EvidenceOwnerType

    record = EvidenceItemRecord(
        id='ev_1',
        owner_type='run',
        owner_id='run_1',
        kind='test_result',
        title='Test result',
        summary='All tests passed',
        artifact_ref=None,
        metadata_json={'passed': 10},
        created_at='2026-08-28T09:00:00Z',
        evidence_severity='info',
        is_completion_grade=True,
        ui_digest_text='All 10 tests passed',
    )
    assert record.evidence_severity == 'info'
    assert record.is_completion_grade is True
    assert record.ui_digest_text == 'All 10 tests passed'
    assert record.kind == 'test_result'

    record2 = EvidenceItemRecord(
        id='ev_2',
        owner_type='run',
        owner_id='run_1',
        kind='test_result',
        title='Warning',
        summary='Some tests skipped',
        artifact_ref=None,
        metadata_json={'skipped': 2},
        created_at='2026-08-28T09:00:00Z',
    )
    assert record2.evidence_severity == 'info'
    assert record2.is_completion_grade is False
    assert record2.ui_digest_text is None

    record3 = EvidenceItemRecord(
        id='ev_3',
        owner_type='run',
        owner_id='run_1',
        kind='test_result',
        title='Critical failure',
        summary='Critical tests failed',
        artifact_ref=None,
        metadata_json={'failed': 5},
        created_at='2026-08-28T09:00:00Z',
        evidence_severity='critical',
        is_completion_grade=False,
        ui_digest_text='5 critical tests failed',
    )
    assert record3.evidence_severity == 'critical'
    assert record3.is_completion_grade is False
    assert record3.ui_digest_text == '5 critical tests failed'


def test_operate_evidence_severity_roundtrips_through_store(tmp_path):
    from eidolon.operate.service import OperateService
    from eidolon.core.evidence import EvidenceStore

    service = OperateService(project_root=tmp_path, db_path=tmp_path / 'operate.db', evidence_store=EvidenceStore(tmp_path / 'evidence.db'))
    started = service.start_objective(user_request='Ship operate kernel', decomposition_mode='multi_stream')
    run = started['run']

    service.emit_evidence(
        owner_type='run',
        owner_id=run.id,
        kind='test_result',
        title='All tests passed',
        summary='10 passed',
        metadata_json={'passed': 10},
        artifact_ref=None,
    )

    evidence_items = service.list_evidence_items(run.id)
    assert len(evidence_items) == 1
    assert evidence_items[0].evidence_severity == 'info'
    assert evidence_items[0].is_completion_grade is False


def test_operate_transition_validators_enforce_expected_rules():
    assert is_valid_run_transition('understanding', 'planning') is True
    assert is_valid_run_transition('planning', 'spawning_work') is True
    assert is_valid_run_transition('acting', 'verifying') is True
    assert is_valid_run_transition('completed', 'acting') is False
    assert is_valid_run_transition('failed', 'understanding') is False

    assert is_valid_subagent_transition('queued', 'running') is True
    assert is_valid_subagent_transition('running', 'completed') is True
    assert is_valid_subagent_transition('completed', 'running') is False
    assert is_valid_subagent_transition('failed', 'queued') is False


def test_operate_store_initializes_schema_and_roundtrips_records(tmp_path):
    db_path = tmp_path / 'operate.db'
    store = OperateStore(db_path)

    with sqlite3.connect(db_path) as conn:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }

    assert {
        'work_sessions',
        'objectives',
        'agent_runs',
        'subagent_runs',
        'blocking_issues',
        'approval_gates',
        'transition_events',
        'evidence_items',
    }.issubset(tables)

    session = store.create_session(
        title='Fix deployment timeout',
        source_kind='chat',
        current_view='operate',
        context_kind='project_candidate',
        entry_message_id='msg_123',
        linked_workspace_id='proj_1',
        surface_reason='user_selected_project',
    )
    objective = store.create_objective(
        session_id=session.id,
        title='Fix deployment timeout',
        user_request='fix deployment timeout',
        normalized_goal='Diagnose and resolve deployment timeout',
        scope_summary='diagnosis, fix, verification',
        decomposition_mode='multi_stream',
        candidate_source='chat_clarification',
        acceptance_state='accepted',
        goal_confidence=0.85,
        clarification_completeness=0.7,
        linked_project_id='proj_1',
    )
    run = store.create_agent_run(
        session_id=session.id,
        objective_id=objective.id,
        state='understanding',
        state_reason='New objective created',
        current_phase='understand',
        next_transition='plan',
        autonomy_mode='bounded_autonomous',
    )
    subagent = store.create_subagent_run(
        parent_run_id=run.id,
        objective_id=objective.id,
        display_name='Verification',
        function_type='verifier',
        mission='Run regression verification',
        state='queued',
        state_reason='Spawned for verification',
        assigned_by='system',
    )
    blocker = store.create_blocking_issue(
        owner_type='run',
        owner_id=run.id,
        category='approval',
        title='Need approval',
        summary='External deployment requires approval',
        requires_user_action=True,
        resolution_hint='Approve or switch to dry-run',
    )
    approval = store.create_approval_gate(
        run_id=run.id,
        title='Deploy to production',
        summary='Would change external state',
        action_type='deploy',
    )
    evidence = store.create_evidence_item(
        owner_type='subagent',
        owner_id=subagent.id,
        kind='test_result',
        title='Regression suite',
        summary='18 passed',
        artifact_ref=None,
        metadata_json={'passed': 18},
    )
    event = store.append_transition_event(
        actor_type='subagent',
        actor_id=subagent.id,
        transition_type='state_change',
        from_state='queued',
        to_state='running',
        summary='Verification started',
        evidence_ids=[evidence.id],
    )

    assert store.get_current_session().id == session.id
    assert store.get_current_run(session.id).id == run.id
    assert store.list_subagent_runs(run.id)[0].id == subagent.id
    assert store.list_blocking_issues(run.id)[0].id == blocker.id
    assert store.list_approval_gates(run.id)[0].id == approval.id
    assert store.list_evidence_items(run.id)[0].id == evidence.id
    assert store.list_transition_events(run.id)[0].id == event.id
