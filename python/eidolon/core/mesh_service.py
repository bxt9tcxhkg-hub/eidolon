"""Mesh-Service für Eidolon — Discovery, Pairing, Verbindungsaufbau."""
from __future__ import annotations

from pathlib import Path

from eidolon.core.config import HTTP_PORT, MESH_DISCOVERY_PORT
from eidolon.core.mesh_identity import host_identity, local_ip
from eidolon.core.mesh_pairing_service import accept_browser_pairing, accept_pairing, create_pairing, unpair_peer
from eidolon.core.mesh_peer_views import is_self_pairing, paired_peers, scan_peers
from eidolon.core.mesh_rendering import generate_qr_png_data_url, generate_qr_svg, qr_debug_info
from eidolon.core.mesh_support import MeshDiscovery, MeshPairing, PeerInfo


class MeshService:
    """Haupt-Service für Mesh-Operationen."""

    def __init__(self, project_root: Path, http_port: int = HTTP_PORT, discovery_port: int = MESH_DISCOVERY_PORT):
        self._root = project_root
        self._http_port = http_port
        self._discovery_port = discovery_port
        self._name = __import__('socket').gethostname()
        self._peer_id, self._public_key = host_identity(project_root)
        self._discovery = MeshDiscovery(discovery_port)
        self._pairing = MeshPairing(project_root)
        self._local_peers: dict[str, PeerInfo] = {}

    @property
    def peer_id(self) -> str: return self._peer_id
    @property
    def public_key(self) -> str: return self._public_key
    @property
    def name(self) -> str: return self._name
    def start(self): self._discovery.start()
    def stop(self): self._discovery.stop()
    def get_local_ip(self) -> str: return local_ip()
    def _is_self_pairing(self, info): return is_self_pairing(self, info)
    def scan_peers(self) -> list[PeerInfo]: return scan_peers(self)
    def create_pairing(self, target_name: str = '', target_address: str = '', target_port: int = 0) -> dict: return create_pairing(self, target_name, target_address, target_port)
    def accept_pairing(self, code: str) -> dict: return accept_pairing(self, code)
    def accept_browser_device_pairing(self, code: str, *, device_name: str, peer_id: str, public_key: str, address: str, user_agent: str = '') -> dict: return accept_browser_pairing(self, code, device_name=device_name, peer_id=peer_id, public_key=public_key, address=address, user_agent=user_agent)
    def get_pending_requests(self) -> list[dict]: return self._pairing.get_pending()
    def get_paired_peers(self) -> list[dict]: return paired_peers(self)
    def unpair_peer(self, peer_id: str) -> dict: return unpair_peer(self, peer_id)
    def generate_qr_svg(self, payload: str) -> str: return generate_qr_svg(payload)
    def generate_qr_png_data_url(self, payload: str) -> str: return generate_qr_png_data_url(payload)
    def qr_debug_info(self, payload: str) -> dict: return qr_debug_info(payload)


_mesh_service: MeshService | None = None


def get_mesh_service(project_root: Path, http_port: int = HTTP_PORT, discovery_port: int = MESH_DISCOVERY_PORT) -> MeshService:
    global _mesh_service
    if _mesh_service is None:
        _mesh_service = MeshService(project_root, http_port, discovery_port)
        _mesh_service.start()
    return _mesh_service
