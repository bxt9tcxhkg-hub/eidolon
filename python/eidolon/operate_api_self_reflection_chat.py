from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI

from eidolon.operate.self_reflection import generate_self_reflection_report
from eidolon.operate.self_reflection.semantic_reflection import SemanticReflector
from eidolon.routes.api_response import api_v1_error, api_v1_ok


def register_self_reflection_chat_route(
    app: FastAPI,
    *,
    get_operate_service,
    get_llm_backend,
) -> None:
    @app.post('/api/v1/self-reflection/chat')
    async def api_v1_self_reflection_chat(request: dict):
        try:
            user_message = request.get('message', '')
            if not user_message:
                return api_v1_error('missing_message', 'Nachricht fehlt', status_code=400)

            # Generate technical report
            from eidolon.core.config import OPERATE_DB, PROJECT_ROOT
            report = generate_self_reflection_report(
                project_root=PROJECT_ROOT / 'python' / 'eidolon',
                docs_root=PROJECT_ROOT / 'docs',
                db_path=OPERATE_DB,
            )

            # Build semantic reflection prompt
            reflector = SemanticReflector()
            reflection_prompt = reflector.reflect(report, user_message)

            # Call LLM with the reflection prompt
            llm_backend = get_llm_backend()
            if llm_backend is None:
                return api_v1_error('llm_unavailable', 'LLM-Backend nicht verfügbar', status_code=503)

            response = await llm_backend.complete(
                system="Du bist Eidolon, ein zentrales agentisches Hauptsystem. Nutze NUR die bereitgestellten Daten für deine Selbstreflexion.",
                user=reflection_prompt,
            )

            if response is None or (isinstance(response, dict) and response.get('error')):
                error_msg = response.get('error', 'Unbekannter Fehler') if isinstance(response, dict) else 'Keine Antwort erhalten'
                return api_v1_error('llm_error', f'LLM-Fehler: {error_msg}', status_code=500)

            response_text = response if isinstance(response, str) else response.get('text', str(response))

            return api_v1_ok({
                'response': response_text,
                'reflection_data': reflector.generate_report_text(report),
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return api_v1_error('reflection_error', f'Selbstreflexion fehlgeschlagen: {str(e)}', status_code=500)
