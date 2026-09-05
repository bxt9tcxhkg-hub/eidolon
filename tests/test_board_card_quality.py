from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.operate.service import OperateService
from eidolon.workspaces.board_seed import SEED_TAG, seed_project_board
from eidolon.workspaces.project_service import ProjectService
from eidolon.workspaces.vorhaben_extract import extract_planning_cards, extract_vorhaben, looks_like_vorhaben
from eidolon.workspaces.workspace_ui_service import WorkspaceUIService

FAMILIEN_NATURAL = (
    'Familienwochenende mit Tesla, 2 Nächte, Unterkunft mit eigenem Bad, CF.'
)
WORKSHOP = (
    'Workshop nächste Woche vorbereiten: Agenda, Raum und Teilnehmer klären.'
)
RELEASE_GATE = (
    'Release vorbereiten: Tests, Changelog und Review. Merge erst nach Review.'
)


def _isolated(tmp_path, monkeypatch):
    ui = WorkspaceUIService(tmp_path)
    ui._project_service = ProjectService(tmp_path)
    ui._operate_service = OperateService(tmp_path)
    monkeypatch.setattr(agent_server, 'workspace_ui_service', ui, raising=False)
    monkeypatch.setattr(agent_server, 'project_service', ui._project_service, raising=False)
    monkeypatch.setattr(agent_server, 'operate_service', ui._operate_service, raising=False)
    return ui


def _titles(cards):
    return [card['title'] for card in cards]


def test_familienwochenende_cards_are_distinct_and_constraint_aware():
    assert looks_like_vorhaben(FAMILIEN_NATURAL) is True
    extracted = extract_vorhaben(FAMILIEN_NATURAL)
    assert extracted is not None
    assert extracted['title'] == 'Familienwochenende'
    titles = _titles(extracted['cards'])
    assert len(titles) == len(set(title.casefold() for title in titles))
    assert any('Anreise' in title and 'Laden' in title for title in titles)
    assert any('Unterkunft' in title and 'Bad' in title for title in titles)
    assert any('Zeitraum' in title for title in titles)
    assert any('Packen' in title or 'Vorbereitung' in title for title in titles)
    assert any('Offene Entscheidungen' in title for title in titles)
    assert not any(title in {'Nächster Schritt', 'Offene Punkte', 'Ort / Rahmen'} for title in titles)
    assert not any(card['description'] == 'Aus dem Vorhaben übernommen.' for card in extracted['cards'])

    by_slot = {card['slot']: card for card in extracted['cards']}
    access = by_slot['access']
    assert 'Tesla' in access['description'] or 'Tesla' in access['facts']
    place = by_slot['place']
    assert any('Bad' in item or 'bad' in item.casefold() for item in place['constraints'] + [place['title'], place['description']])
    when = by_slot['when']
    assert any('2' in item and 'Nächte' in item for item in when['facts'] + [when['description']])
    opened = by_slot['open']
    assert 'CF' in opened['description'] or 'CF' in opened['constraints']
    assert all(card['status'] == 'planned' for card in extracted['cards'])
    assert all(card.get('metadata', {}).get('seed') == 'vorhaben' for card in extracted['cards'])
    assert extracted['approval']['title'] == 'Buchung vorschlagen'


def test_workshop_cards_stay_generic_and_non_travel():
    extracted = extract_vorhaben(WORKSHOP)
    assert extracted is not None
    titles = _titles(extracted['cards'])
    joined = ' '.join(titles)
    assert 'Anreise' not in joined
    assert 'Unterkunft' not in joined
    assert 'Tesla' not in joined
    assert 'Laden' not in joined
    assert any('Agenda' in title for title in titles)
    assert any('Raum' in title for title in titles)
    assert any('Teilnehmer' in title for title in titles)
    assert any('Zeitraum' in title for title in titles)
    assert any('Offene Entscheidungen' in title for title in titles)
    when = next(card for card in extracted['cards'] if card['slot'] == 'when')
    assert 'nächste Woche' in when['description'].casefold() or any('woche' in item.casefold() for item in when['facts'])
    assert extracted['approval'] is None
    assert all(card.get('domain') != 'travel' for card in extracted['cards'])


def test_gate_language_blocks_only_the_implied_card():
    cards = extract_planning_cards(RELEASE_GATE, title='Release')
    titles = _titles(cards)
    assert 'Anreise' not in ' '.join(titles)
    assert any(title == 'Tests' for title in titles)
    assert any(title == 'Changelog' for title in titles)
    review = next(card for card in cards if card['title'] == 'Review')
    assert review['status'] == 'blocked'
    assert all(card['status'] == 'planned' for card in cards if card['title'] != 'Review')


def test_extractor_does_not_invent_facts_absent_from_text():
    cards = extract_planning_cards(FAMILIEN_NATURAL, title='Familienwochenende')
    blob = ' '.join(
        ' '.join([card['title'], card['description'], ' '.join(card['facts']), ' '.join(card['constraints'])])
        for card in cards
    ).casefold()
    for invented in ('supercharger', 'hotel xy', 'berlin', 'kindersitz', 'allergie'):
        assert invented not in blob


def test_seed_is_idempotent_and_keeps_user_cards(tmp_path):
    service = ProjectService(tmp_path)
    project = service.create_project('Familienwochenende', FAMILIEN_NATURAL)
    first = seed_project_board(service, project, FAMILIEN_NATURAL)
    assert len(first) >= 4
    project = service.get_project(project.id)
    first_titles = [item.title for item in project.elements]
    assert len(first_titles) == len(set(title.casefold() for title in first_titles))
    assert all(SEED_TAG in (item.tags or []) for item in project.elements)
    second = seed_project_board(service, project, FAMILIEN_NATURAL)
    assert second == []
    project = service.get_project(project.id)
    assert [item.title for item in project.elements] == first_titles

    user_card = service.add_element(project.id, title='Eigene Notiz', description='vom Nutzer', status='planned', element_type='task')
    third = seed_project_board(service, project, FAMILIEN_NATURAL)
    assert third == []
    project = service.get_project(project.id)
    titles = [item.title for item in project.elements]
    assert titles.count('Eigene Notiz') == 1
    assert titles.count(first_titles[0]) == 1
    renamed = service.update_element(project.id, first[0].id, title='Fahrt klären')
    assert renamed is not None
    fourth = seed_project_board(service, project, FAMILIEN_NATURAL)
    project = service.get_project(project.id)
    titles = [item.title for item in project.elements]
    assert 'Fahrt klären' in titles
    assert titles.count(first[0].title) <= 1
    assert user_card.id in {item.id for item in project.elements}


def test_confirm_natural_familienwochenende_seeds_readable_board(tmp_path, monkeypatch):
    ui = _isolated(tmp_path, monkeypatch)

    async def boom(*_args, **_kwargs):
        raise RuntimeError('connection refused: ollama down')

    monkeypatch.setattr(agent_server.llm_backend, 'complete', boom)
    client = TestClient(agent_server.app)
    chat = client.post('/chat', json={'message': FAMILIEN_NATURAL, 'source': 'chat'})
    assert chat.status_code == 200
    formation = chat.json()['runtime_context']['formation']
    assert formation.get('visible') is True
    assert formation.get('current_state') == 'project_candidate'
    assert formation.get('action_label') == 'Ja, übernehmen'
    accepted = client.post('/workspaces/formation', json={
        'workspace_id': formation['workspace_id'],
        'to_state': 'active_project',
        'confirmed': True,
        'seed_board': True,
        'reason': 'user_confirmed_promotion',
    })
    assert accepted.status_code == 200
    project = accepted.json()['project']
    titles = [item['title'] for item in project['elements']]
    assert titles, 'empty board after confirm is a failure'
    assert any('Anreise' in title for title in titles)
    assert any('Unterkunft' in title and 'Bad' in title for title in titles)
    assert any('Zeitraum' in title for title in titles)
    tesla_notes = ' '.join(item.get('description') or '' for item in project['elements'])
    assert 'Tesla' in tesla_notes or any('Tesla' in (item.get('domain_data') or {}).get('facts', []) for item in project['elements'])
    assert all(item.get('element_type') == 'task' for item in project['elements'])
    assert not any(item.get('domain') == 'travel' for item in project['elements'])
    assert all(SEED_TAG in (item.get('tags') or []) for item in project['elements'])
    statuses = {item.get('status') for item in project['elements']}
    assert statuses <= {'planned', 'blocked'}
    assert 'planned' in statuses
    again = client.post('/workspaces/formation', json={
        'workspace_id': accepted.json()['workspace']['workspace_id'],
        'to_state': 'active_project',
        'confirmed': True,
        'seed_board': True,
        'reason': 'user_confirmed_promotion',
    })
    assert again.status_code == 200
    again_titles = [item['title'] for item in again.json()['project']['elements']]
    assert again_titles == titles
    session_id = chat.json().get('session_id')
    if session_id:
        agent_server.chat_session_store.delete_session(session_id)
