from __future__ import annotations

import asyncio
import threading


def start_background(quic_server) -> bool:
    def runner() -> None:
        asyncio.run(quic_server.serve_forever())
    quic_server._thread = threading.Thread(target=runner, daemon=True)
    quic_server._thread.start()
    return True


def start_foreground(quic_server) -> bool:
    asyncio.run(quic_server.start())
    return True


def stop_sync(quic_server) -> None:
    asyncio.run(quic_server.stop())
