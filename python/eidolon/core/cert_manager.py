"""mTLS-Zertifikatsverwaltung für Eidolon."""
from __future__ import annotations

from pathlib import Path

from eidolon.core.cert_generation import generate_ca, issue_leaf
from eidolon.core.cert_paths import CertificatePaths
from eidolon.core.cert_status import build_status, inspect_certificate, is_ca
from eidolon.core.cert_verify import verify_chain


class CertificateManager:
    """Verwaltet CA und daraus abgeleitete Zertifikate."""

    def __init__(self, project_root: Path):
        self._paths = CertificatePaths(project_root)
        self._root = self._paths.root
        self._dir = self._paths.dir
        self.ca_cert = self._paths.ca_cert
        self.ca_key = self._paths.ca_key
        self.server_cert = self._paths.server_cert
        self.server_key = self._paths.server_key
        self.client_cert = self._paths.client_cert
        self.client_key = self._paths.client_key

    def status(self) -> dict:
        return build_status(self._paths)

    def inspect(self, path: Path) -> dict:
        return inspect_certificate(path)

    @staticmethod
    def _is_ca(cert) -> bool:
        return is_ca(cert)

    def generate_ca(self, days: int = 3650, force: bool = False) -> dict:
        return generate_ca(self._paths, days=days, force=force)

    def _issue(self, cn: str, cert_path: Path, key_path: Path, server_auth: bool, days: int, extra_sans: list[str] | None = None) -> dict:
        return issue_leaf(self._paths, cn, cert_path, key_path, server_auth=server_auth, days=days, extra_sans=extra_sans)

    def generate_server(self, days: int = 825, force: bool = False) -> dict:
        if self.server_cert.exists() and not force:
            return {'ok': True, 'skipped': True, 'reason': 'Server-Zertifikat existiert bereits'}
        return self._issue('eidolon-server', self.server_cert, self.server_key, server_auth=True, days=days)

    def generate_client(self, days: int = 825, force: bool = False) -> dict:
        if self.client_cert.exists() and not force:
            return {'ok': True, 'skipped': True, 'reason': 'Client-Zertifikat existiert bereits'}
        return self._issue('eidolon-client', self.client_cert, self.client_key, server_auth=False, days=days)

    def generate_all(self, force: bool = False) -> dict:
        return {'ok': True, 'ca': self.generate_ca(force=force), 'server': self.generate_server(force=force), 'client': self.generate_client(force=force), 'status': self.status()}

    def verify_chain(self) -> dict:
        return verify_chain(self._paths)


_manager: CertificateManager | None = None


def get_certificate_manager(project_root: Path) -> CertificateManager:
    global _manager
    if _manager is None:
        _manager = CertificateManager(project_root)
    return _manager
