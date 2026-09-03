from __future__ import annotations

from typing import Any

from eidolon.work_context_kernel import build_unified_work_context


def build_runtime_context(message: str, session: dict[str, Any] | None, source: str, workspace_payload: dict[str, Any] | None, llm_status: dict[str, Any] | None, capability_payload: list[dict[str, Any]] | None, user_model: dict[str, Any] | None, operate_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_unified_work_context(
        message=message,
        session=session,
        source=source,
        workspace_payload=workspace_payload,
        llm_status=llm_status,
        capability_payload=capability_payload,
        user_model=user_model,
        operate_snapshot=operate_snapshot,
    )
