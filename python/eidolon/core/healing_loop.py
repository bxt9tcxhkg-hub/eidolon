from __future__ import annotations

import asyncio


async def loop(service) -> None:
    while service._running:
        try:
            await service.run_check_cycle()
        except Exception:
            pass
        await asyncio.sleep(service.check_interval)
