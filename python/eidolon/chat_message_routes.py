from __future__ import annotations

from fastapi import FastAPI

from eidolon.chat_error_support import sanitize_chat_error
from eidolon.chat_route_support import session_payload, truth_quality
from eidolon.chat_turn_status import PHASE_ANTWORTET, PHASE_DENKT, set_chat_turn_phase
from eidolon.core.llm_backend import configure_from_settings
from eidolon.core.settings_apply import apply_user_settings, format_settings_apply_reply
from eidolon.core.settings_intent import parse_settings_intent


def _mark_chat_phase(session_id: str | None, phase: str, reason: str) -> None:
    set_chat_turn_phase(session_id, phase, reason)


def register_chat_routes(app: FastAPI, *, chat_session_store, llm_backend, settings_store, topic_attention_store, build_chat_prompts, build_grounded_fallback_reply, finalize_chat_reply, system_prompt: str, chat_runtime_payload, chat_runtime_truth_reply) -> None:
    @app.post('/chat')
    async def chat(request: dict):
        message = request.get('message', '')
        source = request.get('source', 'chat')
        requested_session_id = str(request.get('session_id') or '').strip() or None
        if not message:
            return {'ok': False, 'error': 'Keine Nachricht'}
        session = chat_session_store.ensure_session(requested_session_id, source=source)
        session_id = session.get('session_id')
        _mark_chat_phase(session_id, PHASE_DENKT, 'build_runtime_context')
        chat_session_store.append_message(session_id, 'user', message, source=source)
        session, runtime_context = session_payload(chat_session_store, session_id, source, message, chat_runtime_payload)
        truth_reply = chat_runtime_truth_reply(message, runtime_context)
        if truth_reply is not None:
            quality = truth_quality(runtime_context)
            _mark_chat_phase(session_id, PHASE_ANTWORTET, 'runtime_truth_reply')
            chat_session_store.append_message(session_id, 'assistant', truth_reply)
            return {'ok': True, 'response': truth_reply, 'provider': llm_backend.status(), 'session_id': session_id, 'runtime_context': runtime_context, 'response_quality': quality}
        settings_intent = parse_settings_intent(message)
        if settings_intent is not None:
            result = apply_user_settings(
                settings_store,
                settings_intent,
                after_llm=lambda: configure_from_settings(settings_store.get_area('llm'), llm_backend),
            )
            reply = format_settings_apply_reply(result, llm_backend.status())
            quality = {**truth_quality(runtime_context), 'path': 'settings_apply', 'settings_applied': bool(result.get('applied'))}
            runtime_context = {**runtime_context, 'settings_apply': {'ok': result.get('ok'), 'applied': result.get('applied'), 'area': result.get('area'), 'updated': result.get('updated') or [], 'error': result.get('error')}}
            _mark_chat_phase(session_id, PHASE_ANTWORTET, 'settings_apply_reply')
            chat_session_store.append_message(session_id, 'assistant', reply)
            return {'ok': bool(result.get('ok')), 'response': reply, 'provider': llm_backend.status(), 'session_id': session_id, 'runtime_context': runtime_context, 'response_quality': quality, 'settings_apply': runtime_context['settings_apply']}
        topic_attention_store.record_interaction(message, source=source)
        try:
            area = settings_store.get_area('llm')
            base_prompt = str(area.get('system_prompt') or '').strip() or system_prompt
            compiled_system_prompt, user_prompt = build_chat_prompts(base_prompt, runtime_context)
            _mark_chat_phase(session_id, PHASE_DENKT, 'llm_complete')
            reply = await llm_backend.complete(compiled_system_prompt, user_prompt)
            _mark_chat_phase(session_id, PHASE_ANTWORTET, 'finalize_reply')
            reply, quality = finalize_chat_reply(reply, runtime_context)
            if not str(reply).strip():
                reply = build_grounded_fallback_reply(runtime_context)
                quality['used_fallback'] = True
                quality['contract_satisfied'] = True
        except Exception as exc:
            assistant_message, public_error, error_code = sanitize_chat_error(exc)
            _mark_chat_phase(session_id, PHASE_ANTWORTET, 'chat_error')
            chat_session_store.append_message(session_id, 'assistant', f'Fehler: {assistant_message}')
            return {'ok': False, 'error': public_error, 'error_code': error_code, 'session_id': session_id, 'runtime_context': runtime_context}
        chat_session_store.append_message(session_id, 'assistant', reply)
        return {'ok': True, 'response': reply, 'provider': llm_backend.status(), 'session_id': session_id, 'runtime_context': runtime_context, 'response_quality': quality}
