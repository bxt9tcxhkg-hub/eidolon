from __future__ import annotations

from eidolon.browser_control_actions import click, extract, list_sessions, navigate, screenshot, session_status, type_text
from eidolon.browser_control_sessions import availability_probe, start_session, stop_session
from eidolon.core.config import DATA_DIR


class BrowserControlService:
    def __init__(self) -> None:
        self._sessions: dict[str, object] = {}
        self._artifacts_dir = DATA_DIR / 'browser'
        self._artifacts_dir.mkdir(parents=True, exist_ok=True)

    async def is_available(self) -> tuple[bool, str]:
        return await availability_probe()

    async def start(self, *, url: str = 'https://example.com', headless: bool = True) -> dict:
        session_id = await start_session(self, url=url, headless=headless)
        return await self.status(session_id)

    async def stop(self, session_id: str) -> dict:
        return await stop_session(self, session_id)

    async def status(self, session_id: str) -> dict:
        return await session_status(self, session_id)

    async def navigate(self, session_id: str, url: str) -> dict:
        return await navigate(self, session_id, url)

    async def extract(self, session_id: str, selector: str = 'body') -> dict:
        return await extract(self, session_id, selector)

    async def click(self, session_id: str, selector: str) -> dict:
        return await click(self, session_id, selector)

    async def type(self, session_id: str, selector: str, text: str, submit: bool = False) -> dict:
        return await type_text(self, session_id, selector, text, submit)

    async def screenshot(self, session_id: str) -> dict:
        return await screenshot(self, session_id)

    async def list_sessions(self) -> dict:
        return await list_sessions(self)

    def _require(self, session_id: str):
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f'Unbekannte Browser-Session: {session_id}')
        return session


_service: BrowserControlService | None = None


def get_browser_control_service() -> BrowserControlService:
    global _service
    if _service is None:
        _service = BrowserControlService()
    return _service
