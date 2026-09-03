from __future__ import annotations

from pathlib import Path

from eidolon.core.config import state_path


class CertificatePaths:
    def __init__(self, project_root: Path):
        self.root = Path(project_root)
        self.dir = state_path('mesh', project_root=self.root)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ca_cert = self.dir / 'ca.crt'
        self.ca_key = self.dir / 'ca.key'
        self.server_cert = self.dir / 'server.crt'
        self.server_key = self.dir / 'server.key'
        self.client_cert = self.dir / 'client.crt'
        self.client_key = self.dir / 'client.key'
