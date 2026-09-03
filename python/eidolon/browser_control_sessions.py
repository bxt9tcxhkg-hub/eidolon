from __future__ import annotations

from pathlib import Path
import uuid

from playwright.async_api import async_playwright

from eidolon.browser_control_models import new_session


async def availability_probe() -> tuple[bool, str]:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            await browser.close()
        return True, 'Playwright Async-Chromium startbar'
    except Exception as exc:
        return False, f'Playwright nicht startbar: {exc}'


async def start_session(service, *, url: str = 'https://example.com', headless: bool = True):
    session_id = uuid.uuid4().hex[:12]
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(url, wait_until='load', timeout=30000)
    session = new_session(session_id, playwright, browser, context, page)
    service._sessions[session_id] = session
    return session_id


async def stop_session(service, session_id: str) -> dict:
    session = service._require(session_id)
    try:
        await session.context.close()
        await session.browser.close()
        await session.playwright.stop()
    finally:
        service._sessions.pop(session_id, None)
    return {'ok': True, 'session_id': session_id, 'stopped': True}
