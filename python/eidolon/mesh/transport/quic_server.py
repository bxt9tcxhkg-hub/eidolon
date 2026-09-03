from __future__ import annotations

from pathlib import Path
from typing import Any, Awaitable, Callable
import json

from eidolon.core.config import CERT_DIR, QUIC_PORT
from eidolon.mesh.transport.quic_cert_config import client_configuration, server_configuration
from eidolon.mesh.transport.quic_protocol import stream_handler
from eidolon.mesh.transport.quic_threading import start_background, start_foreground, stop_sync


class EidolonQuicServer:
    def __init__(self, device_id: str = 'host', device_name: str = 'Eidolon Host', host: str = '127.0.0.1', port: int = QUIC_PORT, cert_dir: str | Path | None = None):
        self.device_id = device_id
        self.device_name = device_name
        self.host = host
        self.port = int(port)
        self.cert_dir = Path(cert_dir or CERT_DIR)
        self.on_message: Callable[[bytes], Awaitable[None]] | None = None
        self._server = None
        self._running = False

    async def start(self) -> bool:
        from aioquic.asyncio import serve
        configuration = server_configuration(self.cert_dir)
        self._server = await serve(self.host, self.port, configuration=configuration, stream_handler=lambda r, w: stream_handler(self, r, w))
        self._running = True
        return True

    async def serve_forever(self) -> None:
        import asyncio
        await self.start()
        while self._running:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        self._running = False
        if self._server is not None:
            self._server.close()
            self._server = None


class QUICServer:
    def __init__(self, host: str = '127.0.0.1', port: int = QUIC_PORT, cert_dir: str | Path | None = None):
        self.server = EidolonQuicServer(host=host, port=port, cert_dir=cert_dir)
        self._thread = None

    def start(self, background: bool = True) -> bool:
        return start_background(self.server) if background else start_foreground(self.server)

    def stop(self) -> None:
        if self.server:
            stop_sync(self.server)


class EidolonQuicClient:
    def __init__(self, cert_dir: str | Path | None = None):
        self.cert_dir = Path(cert_dir or CERT_DIR)
        self._ctx = None
        self._connection = None

    async def connect(self, host: str, port: int) -> bool:
        from aioquic.asyncio import connect
        configuration = client_configuration(self.cert_dir)
        self._ctx = connect(host, int(port), configuration=configuration)
        self._connection = await self._ctx.__aenter__()
        return True

    async def send_message(self, payload: dict[str, Any] | bytes) -> bytes | None:
        if self._connection is None:
            return None
        raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode('utf-8')
        reader, writer = await self._connection.create_stream()
        writer.write(raw)
        await writer.drain()
        data = await reader.read(65536)
        writer.close()
        return data

    async def close(self) -> None:
        if self._ctx is not None:
            await self._ctx.__aexit__(None, None, None)
            self._ctx = None
            self._connection = None
