from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass
class CronJob:
    name: str
    interval_seconds: int
    task: Callable[[], Any | Awaitable[Any]]


class Scheduler:
    def __init__(self) -> None:
        self.jobs: list[CronJob] = []
        self._running = False

    def add(self, job: CronJob) -> None:
        self.jobs.append(job)

    async def start(self) -> None:
        self._running = True
        while self._running:
            for job in self.jobs:
                result = job.task()
                if asyncio.iscoroutine(result):
                    await result
            await asyncio.sleep(min(j.interval_seconds for j in self.jobs))
