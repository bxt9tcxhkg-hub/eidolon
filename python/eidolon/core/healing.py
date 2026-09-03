from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Awaitable, Callable

from eidolon.core.config import HEALTH_LOG, PROJECT_ROOT
from eidolon.core.healing_log import append_log
from eidolon.core.healing_loop import loop
from eidolon.core.healing_runtime import attempt_targeted_recovery, run_check_cycle


class SelfHealingService:
    def __init__(self, project_root: str | Path | None = None, check_interval: int = 30):
        self.project_root = Path(project_root or PROJECT_ROOT)
        self.check_interval = check_interval
        self._running = False
        self._task: asyncio.Task | None = None
        self._checks: dict[str, Callable[[], Awaitable[dict[str, Any]] | dict[str, Any]]] = {}
        self._restart_hooks: dict[str, Callable[[], Awaitable[dict[str, Any]] | dict[str, Any]]] = {}
        self._state = {'running': False, 'check_interval_s': check_interval, 'total_checks': 0, 'total_recoveries': 0, 'error_counts': {}, 'consec_success': {}, 'blocked': {}, 'checks_registered': []}

    def register_restart_hook(self, name: str, fn: Callable[[], Awaitable[dict[str, Any]] | dict[str, Any]]) -> None:
        self._restart_hooks[name] = fn

    async def _recovery_refactor(self) -> dict[str, Any]:
        return {'ok': False, 'strategy': 'not_configured', 'detail': 'Kein Refactor-Recovery-Hook registriert'}

    def register_check(self, name: str, fn: Callable[[], Awaitable[dict[str, Any]] | dict[str, Any]], restart_hook: Callable[[], Awaitable[dict[str, Any]] | dict[str, Any]] | None = None) -> None:
        self._checks[name] = fn
        if restart_hook:
            self._restart_hooks[name] = restart_hook
        self._state['checks_registered'] = sorted(self._checks.keys())
        self._state['consec_success'].setdefault(name, 0)

    def _append_log(self, entry: dict[str, Any]) -> None:
        append_log(Path(HEALTH_LOG), entry)

    async def run_check_cycle(self) -> dict[str, Any]:
        return await run_check_cycle(self)

    async def attempt_targeted_recovery(self, check_name: str) -> dict[str, Any]:
        return await attempt_targeted_recovery(self, check_name)

    async def _loop(self) -> None:
        await loop(self)

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._state['running'] = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self._running = False
        self._state['running'] = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None

    def get_state(self) -> dict[str, Any]:
        self._state['running'] = self._running
        self._state['check_interval_s'] = self.check_interval
        self._state['checks_registered'] = sorted(self._checks.keys())
        return dict(self._state)
