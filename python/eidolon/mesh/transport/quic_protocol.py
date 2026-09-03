from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Awaitable, Callable


async def handle_stream(server, reader, writer) -> None:
    try:
        data = await reader.read(65536)
        if data and server.on_message:
            await server.on_message(data)
        if data:
            try:
                payload = json.loads(data.decode('utf-8'))
            except Exception:
                payload = {'raw': data.decode('utf-8', errors='replace')}
            response = {'from': server.device_id, 'device_name': server.device_name, 'type': payload.get('type', 'mesh_message'), 'received_at': datetime.utcnow().isoformat(), 'echo': payload}
            writer.write(json.dumps(response).encode('utf-8'))
            await writer.drain()
    finally:
        writer.close()


def stream_handler(server, reader, writer) -> None:
    import asyncio
    asyncio.create_task(handle_stream(server, reader, writer))
