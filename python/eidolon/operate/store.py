from __future__ import annotations

from eidolon.operate.store_foundation import OperateStoreFoundation
from eidolon.operate.store_rows import OperateStoreRowMappers
from eidolon.operate.store_run_state import OperateStoreRunStateMixin
from eidolon.operate.store_session_objective import OperateStoreSessionObjectiveMixin


class OperateStore(
    OperateStoreSessionObjectiveMixin,
    OperateStoreRunStateMixin,
    OperateStoreFoundation,
    OperateStoreRowMappers,
):
    pass
