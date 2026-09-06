"""Everyday-path vs. Mehr/Settings layering.

Chat / Projekte / Arbeit are the default door. Technique and system
panels stay reachable under Mehr, with honest German labels.
"""

from __future__ import annotations

from typing import Iterable

# Everyday path: conversation, cards/board, one action.
PRIMARY_TABS: tuple[dict, ...] = (
    {
        'tab': 'chat',
        'nav_label': 'Chat',
        'mobile_label': 'Chat',
        'title': 'Eidolon',
        'subtitle': 'Starte ein Gespräch oder setze reale Arbeit fort.',
        'layer': 'primary',
    },
    {
        'tab': 'workspaces',
        'nav_label': 'Projekte',
        'mobile_label': 'Projekte',
        'title': 'Projekte',
        'subtitle': 'Karten zum Planen — oder ein neues Projekt anlegen',
        'layer': 'primary',
    },
    {
        'tab': 'operate',
        'nav_label': 'Arbeit',
        'mobile_label': 'Arbeit',
        'title': 'Arbeit',
        'subtitle': 'Freigaben und nächster Schritt, sobald etwas läuft',
        'layer': 'primary',
    },
)

# Honesty tokens for catalog-only / ledger-only Mehr items (K3 / M3).
HONESTY_HINTS = {
    'catalog': 'nicht ausführbar',
    'ledger': 'keine eigenen Prozesse',
}

MORE_GROUPS: tuple[dict, ...] = (
    {
        'id': 'betrieb',
        'title': 'Betrieb',
        'items': (
            {
                'tab': 'settings',
                'nav_label': 'Einstellungen',
                'mobile_label': 'Einstellungen',
                'title': 'Einstellungen',
                'subtitle': 'Konfiguration mit speicherbaren Werten und Herkunftsanzeige',
                'icon': '⚙️',
                'layer': 'more',
                'group': 'config',
            },
            {
                'tab': 'settings',
                'nav_label': 'KI-Verbindung',
                'mobile_label': 'KI-Verbindung',
                'title': 'Einstellungen',
                'subtitle': 'Anbieter, Ersatzkette und Verbindungsstatus — keine Chat-Diagnosewand',
                'icon': '🧠',
                'layer': 'more',
                'group': 'config',
                'settings_area': 'llm',
                'highlight_tab': False,
            },
            {
                'tab': 'mesh',
                'nav_label': 'Geräte (Mesh)',
                'mobile_label': 'Geräte (Mesh)',
                'title': 'Geräte',
                'subtitle': 'Mesh: Handy, Browser und weitere Geräte mit Eidolon koppeln',
                'icon': '📡',
                'layer': 'more',
                'group': 'advanced',
            },
            {
                'tab': 'identity',
                'nav_label': 'Identität',
                'mobile_label': 'Identität',
                'title': 'Identität',
                'subtitle': 'Rollenmodell und Produkt-Selbstbeschreibung',
                'icon': '🪞',
                'layer': 'more',
                'group': 'config',
            },
            {
                'tab': 'backups',
                'nav_label': 'Sicherungen',
                'mobile_label': 'Sicherungen',
                'title': 'Sicherungen',
                'subtitle': 'Echte Wiederherstellungspunkte und Speicherzustand',
                'icon': '💾',
                'layer': 'more',
                'group': 'advanced',
            },
        ),
    },
    {
        'id': 'technik',
        'title': 'Technik',
        'items': (
            {
                'tab': 'dashboard',
                'nav_label': 'Systemstatus',
                'mobile_label': 'Systemstatus',
                'title': 'Systemstatus',
                'subtitle': 'Health, Capability-Prüfungen, Laufzeit und Speicher',
                'icon': '📊',
                'layer': 'more',
                'group': 'advanced',
            },
            {
                'tab': 'healing',
                'nav_label': 'Healing',
                'mobile_label': 'Healing',
                'title': 'Healing',
                'subtitle': 'Health-Checks und gemeldeter Status — Wiederherstellung nur wo verdrahtet',
                'icon': '🩹',
                'layer': 'more',
                'group': 'advanced',
            },
            {
                'tab': 'skills',
                'nav_label': 'Fähigkeiten-Katalog',
                'mobile_label': 'Fähigkeiten-Katalog',
                'title': 'Fähigkeiten-Katalog',
                'subtitle': 'Katalog hinterlegter Fähigkeiten — ausführbar nur im Chat, wo verdrahtet',
                'icon': '⚡',
                'layer': 'more',
                'group': 'advanced',
                'honesty': 'catalog',
            },
            {
                'tab': 'code',
                'nav_label': 'Code-Reparatur',
                'mobile_label': 'Code-Reparatur',
                'title': 'Code-Reparatur',
                'subtitle': 'Gezielte Analyse und Reparatur von lokalen Eidolon-Dateien',
                'icon': '🔧',
                'layer': 'more',
                'group': 'advanced',
            },
            {
                'tab': 'goals',
                'nav_label': 'Autonomie-Ziele',
                'mobile_label': 'Autonomie-Ziele',
                'title': 'Autonomie-Ziele',
                'subtitle': 'Systemziele, die Eidolon selbst verfolgt — keine Alltags-Todos',
                'icon': '🎯',
                'layer': 'more',
                'group': 'advanced',
            },
            {
                'tab': 'pods',
                'nav_label': 'Helfer-Protokoll',
                'mobile_label': 'Helfer-Protokoll',
                'title': 'Helfer-Protokoll',
                'subtitle': 'Protokollierte Hilfsläufe — keine eigenen Prozesse',
                'icon': '📋',
                'layer': 'more',
                'group': 'advanced',
                'honesty': 'ledger',
            },
            {
                'tab': 'execution',
                'nav_label': 'Ausführung',
                'mobile_label': 'Ausführung',
                'title': 'Ausführung',
                'subtitle': 'Geräte, Capability-Prüfungen und aktuelle Ausführungssignale',
                'icon': '🧭',
                'layer': 'more',
                'group': 'advanced',
            },
        ),
    },
)

MORE_SUMMARY = 'Mehr'
PRIMARY_GROUP_TITLE = 'Start & Arbeit'
CHAT_IDLE_FORBIDDEN_IDS = (
    'health-badge',
    'health-summary',
    'health-problems',
    'capabilities-summary',
    'dash-components',
    'dash-metrics',
    'healing-status',
    'skills-list',
    'llm-connection-status',
    'execution-capabilities',
    'pods-list',
)
CHAT_IDLE_REQUIRED_IDS = (
    'chat-session-title',
    'chat-input',
    'chat-eidolon-presence',
    'chat-idle-prompt',
)


def iter_more_items() -> Iterable[dict]:
    for group in MORE_GROUPS:
        yield from group['items']


def more_surface_tabs() -> tuple[str, ...]:
    tabs = []
    for item in iter_more_items():
        if item.get('highlight_tab') is False:
            continue
        if item['tab'] not in tabs:
            tabs.append(item['tab'])
    return tuple(tabs)


def primary_tabs() -> tuple[str, ...]:
    return tuple(item['tab'] for item in PRIMARY_TABS)


def all_page_entries() -> dict[str, dict]:
    pages: dict[str, dict] = {}
    for item in PRIMARY_TABS:
        pages[item['tab']] = item
    for item in iter_more_items():
        if item.get('highlight_tab') is False:
            continue
        pages[item['tab']] = item
    return pages


def honesty_hint(item: dict) -> str:
    token = item.get('honesty')
    if not token:
        return ''
    return HONESTY_HINTS[token]


def _attr(name: str, value: str) -> str:
    return f'{name}="{value}"'


def _sidebar_item(item: dict, *, active: bool = False) -> str:
    classes = 'nav-item active' if active else 'nav-item'
    attrs = [
        _attr('class', classes),
        _attr('data-tab-target', item['tab']),
        _attr('data-nav-layer', item['layer']),
    ]
    if item.get('highlight_tab', True):
        attrs.insert(1, _attr('data-tab', item['tab']))
    if active:
        attrs.append(_attr('aria-current', 'page'))
    if item.get('settings_area'):
        attrs.append(_attr('data-settings-area', item['settings_area']))
    if item.get('honesty'):
        attrs.append(_attr('data-nav-honesty', item['honesty']))
    return f'<li {" ".join(attrs)}><span class="icon"></span> {item["nav_label"]}</li>'


def render_sidebar_primary(session_rail_html: str) -> str:
    parts = []
    for item in PRIMARY_TABS:
        parts.append(_sidebar_item(item, active=item['tab'] == 'chat'))
        if item['tab'] == 'chat':
            parts.append(session_rail_html.rstrip())
    return '\n'.join(parts)


def render_sidebar_more() -> str:
    blocks = []
    for group in MORE_GROUPS:
        items = '\n'.join(_sidebar_item(item) for item in group['items'])
        blocks.append(
            f'<div class="nav-group-title">{group["title"]}</div>\n'
            f'<ul class="nav-list nav-list-subtle">\n{items}\n</ul>'
        )
    return '\n'.join(blocks)


def render_mobile_bar() -> str:
    parts = []
    for item in PRIMARY_TABS:
        active = ' active' if item['tab'] == 'chat' else ''
        parts.append(
            f'<div class="mitem{active}" data-tab="{item["tab"]}" data-tab-target="{item["tab"]}" data-nav-layer="primary">'
            f'<span class="icon">•</span><span>{item["mobile_label"]}</span></div>'
        )
    parts.append(
        '<div class="mitem" data-tab="more" data-ui-action="toggleMobileMore" data-nav-layer="more">'
        '<span class="icon">⋯</span><span>Mehr</span></div>'
    )
    return '\n        '.join(parts)


def _mobile_item(item: dict) -> str:
    attrs = [
        _attr('class', 'mobile-more-item'),
        _attr('data-tab-target', item['tab']),
        _attr('data-nav-layer', 'more'),
    ]
    if item.get('highlight_tab', True):
        attrs.append(_attr('data-tab', item['tab']))
    if item.get('settings_area'):
        attrs.append(_attr('data-settings-area', item['settings_area']))
    if item.get('honesty'):
        attrs.append(_attr('data-nav-honesty', item['honesty']))
    hint = honesty_hint(item)
    icon = item.get('icon') or ''
    label = f'{icon} {item["mobile_label"]}'.strip()
    if hint:
        body = (
            f'<span class="mobile-more-copy"><span class="mobile-more-label">{label}</span>'
            f'<span class="mobile-more-hint">{hint}</span></span>'
        )
    else:
        body = label
    return f'<div {" ".join(attrs)}>{body}</div>'


def render_mobile_more() -> str:
    blocks = []
    for group in MORE_GROUPS:
        items = '\n            '.join(_mobile_item(item) for item in group['items'])
        blocks.append(
            f'<div class="mobile-more-group" data-nav-group="{group["id"]}">\n'
            f'            <div class="mobile-more-group-title">{group["title"]}</div>\n'
            f'            <div class="mobile-more-grid">\n            {items}\n            </div>\n'
            f'        </div>'
        )
    return '\n        '.join(blocks)


def _replace_marked(html: str, start: str, end: str, inner: str) -> str:
    start_at = html.find(start)
    end_at = html.find(end)
    if start_at < 0 or end_at < 0 or end_at < start_at:
        raise ValueError(f'Nav-Marker fehlen: {start} … {end}')
    return html[: start_at + len(start)] + '\n' + inner + '\n            ' + html[end_at:]


def inject_nav(html: str) -> str:
    rail_start = '<!--EIDOLON_SESSION_RAIL_BEGIN-->'
    rail_end = '<!--EIDOLON_SESSION_RAIL_END-->'
    rail_at = html.find(rail_start)
    rail_end_at = html.find(rail_end)
    if rail_at < 0 or rail_end_at < 0:
        raise ValueError('Session-Rail-Marker fehlen')
    session_rail = html[rail_at: rail_end_at + len(rail_end)]
    html = _replace_marked(
        html,
        '<!--EIDOLON_NAV_SIDEBAR_PRIMARY_BEGIN-->',
        '<!--EIDOLON_NAV_SIDEBAR_PRIMARY_END-->',
        render_sidebar_primary(session_rail),
    )
    html = _replace_marked(
        html,
        '<!--EIDOLON_NAV_SIDEBAR_MORE_BEGIN-->',
        '<!--EIDOLON_NAV_SIDEBAR_MORE_END-->',
        render_sidebar_more(),
    )
    html = _replace_marked(
        html,
        '<!--EIDOLON_NAV_MOBILE_BAR_BEGIN-->',
        '<!--EIDOLON_NAV_MOBILE_BAR_END-->',
        '        ' + render_mobile_bar(),
    )
    html = _replace_marked(
        html,
        '<!--EIDOLON_NAV_MOBILE_MORE_BEGIN-->',
        '<!--EIDOLON_NAV_MOBILE_MORE_END-->',
        '        ' + render_mobile_more(),
    )
    return html
