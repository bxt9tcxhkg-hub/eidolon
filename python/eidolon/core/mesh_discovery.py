from __future__ import annotations

import json
import socket
import threading
import time

from eidolon.core.config import HTTP_PORT, MESH_DISCOVERY_PORT
from eidolon.core.mesh_models import PeerInfo

MESH_VERSION = 'eidolon-mesh/v2'
MESH_MAGIC = b'EIDOLON'


class MeshDiscovery:
    def __init__(self, discovery_port: int = MESH_DISCOVERY_PORT):
        self._port = discovery_port
        self._running = False
        self._socket: socket.socket | None = None
        self._peers: dict[str, PeerInfo] = {}
        self._listener_thread: threading.Thread | None = None

    def start(self):
        if self._running:
            return
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._socket.settimeout(1.0)
        self._running = True
        self._listener_thread = threading.Thread(target=self._listen, daemon=True)
        self._listener_thread.start()

    def stop(self):
        self._running = False
        if self._socket:
            self._socket.close()
            self._socket = None

    def _listen(self):
        while self._running:
            try:
                data, addr = self._socket.recvfrom(1024)
                self._handle_message(data, addr)
            except socket.timeout:
                continue
            except Exception:
                pass

    def _handle_message(self, data: bytes, addr: tuple):
        try:
            msg = json.loads(data.decode('utf-8'))
            if msg.get('type') != 'discovery':
                return
            peer_id = msg.get('peer_id', '')
            if peer_id in self._peers:
                self._peers[peer_id].last_seen = time.time()
                self._peers[peer_id].status = 'connected'
            else:
                self._peers[peer_id] = PeerInfo(
                    peer_id=peer_id,
                    name=msg.get('name', 'Unbekannt'),
                    address=addr[0],
                    port=msg.get('port', HTTP_PORT),
                    public_key=msg.get('public_key', ''),
                    last_seen=time.time(),
                    status='connected',
                )
        except (json.JSONDecodeError, KeyError):
            pass

    def broadcast_presence(self, port: int, peer_id: str, name: str, public_key: str):
        msg = {'type': 'discovery', 'peer_id': peer_id, 'name': name, 'port': port, 'public_key': public_key, 'version': MESH_VERSION, 'timestamp': time.time()}
        data = json.dumps(msg).encode('utf-8')
        try:
            if self._socket:
                self._socket.sendto(data, ('255.255.255.255', self._port))
        except Exception:
            pass

    def get_peers(self) -> list[PeerInfo]:
        now = time.time()
        expired = [pid for pid, peer in self._peers.items() if now - peer.last_seen > 300]
        for pid in expired:
            del self._peers[pid]
        return list(self._peers.values())
