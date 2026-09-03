from __future__ import annotations

from typing import Any

from eidolon.operate.bridge import build_operate_snapshot, sync_operate_with_workspace_payload
from eidolon.work_context_kernel import build_unified_work_context


def sync_workspace_operate(operate_service, data: dict[str, Any]) -> dict[str, Any]:
    sync_operate_with_workspace_payload(operate_service, data)
    return build_operate_snapshot(operate_service)


def build_workspace_work_context(
    registry,
    operate_service,
    data: dict[str, Any],
    *,
    message: str = '',
    session: dict[str, Any] | None = None,
    source: str = 'workspace',
    operate_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    snapshot = operate_snapshot or sync_workspace_operate(operate_service, data)
    return build_unified_work_context(
        message=message,
        session=session,
        source=source,
        workspace_payload=data,
        llm_status=None,
        capability_payload=[],
        user_model=registry.user_model.get(),
        operate_snapshot=snapshot,
    )
