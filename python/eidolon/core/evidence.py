"""Evidence Store — lokaler Wahrheitsspeicher für Eidolon."""
from __future__ import annotations

from pathlib import Path

from eidolon.core.evidence_logging import log_action, log_artifact, log_blocked, log_observation, log_verification
from eidolon.core.evidence_queries import get_actions, get_artifacts, get_blocked, get_claim_verification, get_verifications
from eidolon.core.evidence_store_support import connect, default_db_path, init_schema


class EvidenceStore:
    """SQLite-basierter Evidence Store für belegbare Aussagen."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else default_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        init_schema(self.db_path)

    def _connect(self):
        return connect(self.db_path)

    def log_action(self, command: str, exit_code: int | None = None, stdout: str | None = None, stderr: str | None = None) -> int:
        return log_action(self, command, exit_code=exit_code, stdout=stdout, stderr=stderr)

    def log_observation(self, action_id: int | None, kind: str, description: str, detail: str | None = None) -> int:
        return log_observation(self, action_id, kind, description, detail=detail)

    def log_artifact(self, action_id: int | None, path: str, sha256: str | None = None, size_bytes: int | None = None) -> int:
        return log_artifact(self, action_id, path, sha256=sha256, size_bytes=size_bytes)

    def log_verification(self, action_id: int | None, claim: str, status: str, evidence: str | None = None) -> int:
        return log_verification(self, action_id, claim, status, evidence=evidence)

    def log_blocked(self, claim: str, reason: str, capability: str | None = None) -> int:
        return log_blocked(self, claim, reason, capability=capability)

    def get_verifications(self, status: str | None = None):
        return get_verifications(self, status=status)

    def get_actions(self, limit: int = 20):
        return get_actions(self, limit=limit)

    def get_artifacts(self, limit: int = 20):
        return get_artifacts(self, limit=limit)

    def get_blocked(self):
        return get_blocked(self)

    def get_claim_verification(self, claim: str):
        return get_claim_verification(self, claim)


_default_store: EvidenceStore | None = None


def get_evidence_store() -> EvidenceStore:
    global _default_store
    if _default_store is None:
        _default_store = EvidenceStore()
    return _default_store
