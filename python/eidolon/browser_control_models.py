from __future__ import annotations

from dataclasses import dataclass
import time

from playwright.async_api import Browser, BrowserContext, Page, Playwright


@dataclass
class BrowserSession:
    session_id: str
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page
    created_at: float
    last_error: str = ''


def session_status(session: BrowserSession) -> dict:
    return {'ok': True, 'session_id': session.session_id, 'url': session.page.url, 'title': '', 'headless': session.browser.browser_type.name == 'chromium', 'created_at': session.created_at, 'last_error': session.last_error}


def new_session(session_id: str, playwright: Playwright, browser: Browser, context: BrowserContext, page: Page) -> BrowserSession:
    return BrowserSession(session_id=session_id, playwright=playwright, browser=browser, context=context, page=page, created_at=time.time())
