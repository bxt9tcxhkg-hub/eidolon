from __future__ import annotations

from eidolon.operate.store_run_blocking import OperateStoreBlockingApprovalMixin
from eidolon.operate.store_run_evidence import OperateStoreEvidenceTransitionMixin
from eidolon.operate.store_run_records import OperateStoreRunRecordsMixin


class OperateStoreRunStateMixin(
    OperateStoreRunRecordsMixin,
    OperateStoreBlockingApprovalMixin,
    OperateStoreEvidenceTransitionMixin,
):
    pass
