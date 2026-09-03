from __future__ import annotations

import time


async def session_status(service, session_id: str) -> dict:
    session = service._require(session_id)
    try:
        title = await session.page.title()
        url = session.page.url
    except Exception as exc:
        session.last_error = str(exc)
        title = ''
        url = ''
    return {'ok': True, 'session_id': session.session_id, 'url': url, 'title': title, 'headless': session.browser.browser_type.name == 'chromium', 'created_at': session.created_at, 'last_error': session.last_error}


async def navigate(service, session_id: str, url: str) -> dict:
    session = service._require(session_id)
    await session.page.goto(url, wait_until='load', timeout=30000)
    return await service.status(session_id)


async def extract(service, session_id: str, selector: str = 'body') -> dict:
    session = service._require(session_id)
    page = session.page
    locator = page.locator(selector).first
    text = await locator.inner_text(timeout=5000)
    links = await page.locator('a').evaluate_all("els => els.slice(0,20).map(a => ({text:(a.innerText||'').trim(), href:a.href}))")
    return {'ok': True, 'session_id': session_id, 'url': page.url, 'title': await page.title(), 'selector': selector, 'text': text[:12000], 'links': links}


async def click(service, session_id: str, selector: str) -> dict:
    session = service._require(session_id)
    await session.page.locator(selector).first.click(timeout=10000)
    await session.page.wait_for_load_state('load', timeout=10000)
    return await service.status(session_id)


async def type_text(service, session_id: str, selector: str, text: str, submit: bool = False) -> dict:
    session = service._require(session_id)
    loc = session.page.locator(selector).first
    await loc.fill(text, timeout=10000)
    if submit:
        await loc.press('Enter')
        await session.page.wait_for_load_state('load', timeout=10000)
    return await service.status(session_id)


async def screenshot(service, session_id: str) -> dict:
    session = service._require(session_id)
    path = service._artifacts_dir / f'{session_id}_{int(time.time())}.png'
    await session.page.screenshot(path=str(path), full_page=True)
    return {'ok': True, 'session_id': session_id, 'path': str(path), 'url': session.page.url, 'title': await session.page.title()}


async def list_sessions(service) -> dict:
    out = []
    for session_id in list(service._sessions.keys()):
        try:
            out.append(await service.status(session_id))
        except KeyError:
            pass
    return {'ok': True, 'sessions': out}
