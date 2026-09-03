"""Mesh-Service für Eidolon — Discovery, Pairing, Verbindungsaufbau."""
from __future__ import annotations

from eidolon.core.mesh_crypto import MeshCrypto
from eidolon.core.mesh_discovery import MESH_MAGIC, MESH_VERSION, MeshDiscovery
from eidolon.core.mesh_models import PairingRequest, PeerInfo
from eidolon.core.mesh_pairing import MeshPairing as MeshPairingCore


class MeshPairing(MeshPairingCore):
    def unpair(self, peer_id: str) -> bool:
        return super().unpair(peer_id)


__all__ = [
    'MESH_MAGIC',
    'MESH_VERSION',
    'MeshCrypto',
    'MeshDiscovery',
    'MeshPairing',
    'PairingRequest',
    'PeerInfo',
]
