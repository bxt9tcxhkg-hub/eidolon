from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI

from eidolon.chat_message_routes import register_chat_routes
from eidolon.chat_session_routes import register_chat_session_routes
from eidolon.code_mutation_routes import register_code_routes


def register_chat_and_code_routes(
    app: FastAPI,
    *,
    chat_session_store,
    llm_backend,
    settings_store,
    topic_attention_store,
    build_chat_prompts,
    build_grounded_fallback_reply,
    finalize_chat_reply,
    system_prompt: str,
    chat_runtime_payload: Callable[[str, str, dict[str, Any] | None], dict[str, Any]],
    latest_session_user_message: Callable[[dict[str, Any] | None], str],
    chat_runtime_truth_reply: Callable[[str], str | None],
    self_reflect_candidates: Callable[[int], list[dict[str, Any]]],
    apply_llm_code_mutation: Callable[..., Any],
    code_analyzer,
    project_root: Path,
) -> None:
    register_chat_session_routes(app, chat_session_store=chat_session_store, latest_session_user_message=latest_session_user_message, chat_runtime_payload=chat_runtime_payload)
    register_chat_routes(app, chat_session_store=chat_session_store, llm_backend=llm_backend, settings_store=settings_store, topic_attention_store=topic_attention_store, build_chat_prompts=build_chat_prompts, build_grounded_fallback_reply=build_grounded_fallback_reply, finalize_chat_reply=finalize_chat_reply, system_prompt=system_prompt, chat_runtime_payload=chat_runtime_payload, chat_runtime_truth_reply=chat_runtime_truth_reply)
    register_code_routes(app, apply_llm_code_mutation=apply_llm_code_mutation, code_analyzer=code_analyzer, self_reflect_candidates=self_reflect_candidates, project_root=project_root)
