from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
import agent_server
from eidolon.chat_quality_fallbacks import build_grounded_fallback_reply
from eidolon.chat_quality_finalize import finalize_chat_reply
from eidolon.chat_runtime_prompting import build_chat_prompts
from eidolon.web_routes import read_root_html

ROOT = Path(__file__).resolve().parents[1]
CHAT_UI_JS = ROOT / 'python' / 'eidolon' / 'web' / 'chat-ui.js'
THREAD_CSS = ROOT / 'python' / 'eidolon' / 'web' / 'components' / 'chat' / 'chat-thread.css'


def _html():
    return read_root_html(ROOT)


def _work_context(**overrides):
    context = {
        'user_intent': {
            'classification': 'continue_existing_work',
            'is_work_oriented': True,
            'latest_message': 'setz das um',
        },
        'workflow_state': {
            'current_context_state': 'active_project',
            'current_phase': 'execute',
            'next_step': 'Antwortpolitik härten',
        },
        'project_context': {
            'active_project_title': 'Chat-Logik härten',
            'active_project_id': 'project_chat_logic',
        },
        'session_context': {'message_count': 3},
        'workspace_context': {
            'active_workspace': {'next_actions': ['Antwortpolitik härten']},
            'candidate_workspace': {},
            'visible_suggestions': [],
        },
    }
    context.update(overrides)
    return context


def test_work_prompt_is_brief_cowork_without_essay_schema():
    system, user = build_chat_prompts('Du bist Eidolon.', _work_context())
    assert 'höchstens 3–5 kurzen Zeilen' in system
    assert 'Höchstens eine nächste Aktion oder eine Klärungsfrage' in system
    assert 'lege ich als Karte an' in system
    assert '2-4 plausible Richtungen' not in system
    assert 'wahrscheinliche Intention' not in system
    assert 'begründete Empfehlung' not in system
    assert 'Erfinde keinen Projektzustand' in system
    assert 'SESSION_VERLAUF:' in user
    assert 'setz das um' in user


def test_casual_prompt_stays_natural_and_not_project_pushed():
    system, _user = build_chat_prompts('Du bist Eidolon.', {
        'user_intent': {
            'classification': 'casual_chat',
            'is_work_oriented': False,
            'latest_message': 'lass uns ein bisschen plaudern',
        },
    })
    assert 'normaler Gesprächspartner' in system
    assert 'nicht automatisch in Projektarbeit' in system
    assert 'höchstens 3–5 kurzen Zeilen' not in system
    assert 'lege ich als Karte an' not in system


def test_work_fallback_is_short_and_offers_one_board_move():
    reply = build_grounded_fallback_reply(_work_context())
    lines = [line for line in reply.splitlines() if line.strip()]
    assert len(lines) <= 5
    assert 'Sinnvolle Richtungen jetzt:' not in reply
    assert 'Ich empfehle:' not in reply
    assert 'Konkreter nächster Schritt:' not in reply
    assert 'Lege ich als Karte an' in reply


def test_finalize_replaces_work_essay_schema_with_short_fallback():
    essay = (
        'Intention: die Chat-Logik härten.\n\n'
        'Sinnvolle Richtungen jetzt:\n'
        '- Richtung A\n- Richtung B\n\n'
        'Ich empfehle: Richtung A.\n'
        'Konkreter nächster Schritt: alles aufschreiben.'
    )
    reply, quality = finalize_chat_reply(essay, _work_context())
    assert quality['essay_schema'] is True
    assert quality['used_fallback'] is True
    assert 'Sinnvolle Richtungen jetzt:' not in reply
    assert 'Lege ich als Karte an' in reply
    assert len([line for line in reply.splitlines() if line.strip()]) <= 5


def test_idle_chat_door_is_title_composer_and_one_project_line():
    html = _html()
    js = CHAT_UI_JS.read_text(encoding='utf-8')
    css = THREAD_CSS.read_text(encoding='utf-8')
    assert 'id="chat-session-title"' in html
    assert 'id="chat-input"' in html
    assert 'id="chat-project-door"' in html
    assert 'function renderChatProjectDoor' in js
    assert "escapeHtml(title) + ' · öffnen</button>'" in js
    assert 'id="chat-landing-panels"' not in html
    assert 'Gerade aktiv' not in html
    assert 'Braucht deine Entscheidung' not in html
    assert 'Arbeitskontext' not in html
    assert 'id="chat-runtime-problems"' not in html
    assert 'chat-home-hero' not in html
    assert 'eidolon-signature hero' not in html
    assert '.chat-project-door' in css
    assert 'id="panel-operate"' in html
    assert 'id="operate-approvals"' in html


def test_chat_http_work_prompt_carries_brief_contract(monkeypatch):
    client = TestClient(agent_server.app)
    captured = {}

    async def fake_complete(system: str, user: str) -> str:
        captured['system'] = system
        return 'Im Projekt weiter.\nLege ich als Karte an.'

    monkeypatch.setattr(agent_server.llm_backend, 'complete', fake_complete)
    response = client.post('/chat', json={'message': 'setz das um', 'source': 'test-stewardship-prompt'})
    assert response.status_code == 200
    body = response.json()
    assert body['ok'] is True
    assert 'höchstens 3–5 kurzen Zeilen' in captured['system']
    assert 'Kein Schema aus Intention, Richtungen oder Empfehlung' in captured['system']
    client.delete(f"/chat/sessions/{body['session_id']}")
