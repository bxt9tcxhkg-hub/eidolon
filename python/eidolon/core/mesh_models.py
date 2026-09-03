from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class PeerInfo:
    peer_id: str
    name: str
    address: str
    port: int
    public_key: str
    last_seen: float
    status: str
    latency_ms: float = 0.0
    paired: bool = False

    def to_dict(self) -> dict:
        return {
            'peer_id': self.peer_id,
            'name': self.name,
            'address': self.address,
            'port': self.port,
            'last_seen': datetime.fromtimestamp(self.last_seen, tz=timezone.utc).isoformat(),
            'status': self.status,
            'latency_ms': self.latency_ms,
            'paired': self.paired,
        }


@dataclass
class PairingRequest:
    code: str
    peer_id: str
    name: str
    address: str
    port: int
    public_key: str
    created_at: float
    expires_at: float
    status: str = 'pending'
