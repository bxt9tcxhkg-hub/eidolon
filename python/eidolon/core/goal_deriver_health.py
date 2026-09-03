from __future__ import annotations

from typing import Any

from eidolon.core.goal_deriver_keys import KEY_CAP_PREFIX, KEY_CERTIFICATES


def from_capabilities(health: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    caps = health.get('components', {}).get('capabilities', {}).get('capabilities', [])
    for cap in caps:
        if cap.get('available'):
            continue
        cid = cap.get('id', 'unbekannt')
        out.append({
            'problem_key': f'{KEY_CAP_PREFIX}{cid}',
            'title': f'Capability aktivieren: {cid}',
            'description': f"{cap.get('name', cid)} ist nicht verfügbar. Grund: {cap.get('detail', 'unbekannt')}",
            'category': 'development',
            'priority': 2,
            'source': f'health:capabilities:{cid}',
            'evidence': cap.get('detail', ''),
            'steps': [
                f"Ursache prüfen: {cap.get('detail', 'unbekannt')}",
                'Abhängigkeit oder Modell bereitstellen',
                f'Verifizieren: {cid} meldet available=true',
            ],
        })
    return out


def verify_capability(health: dict[str, Any], cid: str) -> tuple[bool, str]:
    caps = health.get('components', {}).get('capabilities', {}).get('capabilities', [])
    for cap in caps:
        if cap.get('id') == cid:
            if cap.get('available'):
                return False, f'{cid} ist verfügbar'
            return True, cap.get('detail', 'nicht verfügbar')
    return False, f'{cid} nicht mehr in der Capability-Liste'


def certificate_problem(health: dict[str, Any]) -> dict[str, Any] | None:
    certs = health.get('components', {}).get('certificates', {})
    missing = []
    if not certs.get('ca_exists'):
        missing.append('ca.crt/ca.key')
    if not certs.get('cert_exists'):
        missing.append('server.crt')
    if not certs.get('key_exists'):
        missing.append('server.key')
    expired = bool(certs.get('expired'))
    chain_broken = certs.get('cert_exists') and certs.get('chain_valid') is False
    days_left = certs.get('days_left')
    expiring_soon = isinstance(days_left, int) and 0 <= days_left < 30
    if not (missing or expired or chain_broken or expiring_soon):
        return None
    if missing:
        return {'reason': f"Fehlend: {', '.join(missing)}", 'priority': 4, 'steps': ['CA-Schlüsselpaar erzeugen', 'Server-Zertifikat signieren', 'QUIC-Modus auf strict verifizieren']}
    if expired:
        return {'reason': f'Server-Zertifikat abgelaufen (seit {abs(days_left)} Tagen)', 'priority': 5, 'steps': ['Zertifikat neu ausstellen', 'Kette verifizieren', 'Peers neu pairen']}
    if chain_broken:
        return {'reason': 'Server-Zertifikat ist nicht von der eigenen CA signiert', 'priority': 5, 'steps': ['Kette analysieren', 'Zertifikat neu signieren', 'verify_chain prüfen']}
    return {'reason': f'Server-Zertifikat läuft in {days_left} Tagen ab', 'priority': 3, 'steps': ['Zertifikat erneuern', 'Kette verifizieren']}


def from_certificates(health: dict[str, Any]) -> list[dict[str, Any]]:
    problem = certificate_problem(health)
    if not problem:
        return []
    certs = health.get('components', {}).get('certificates', {})
    return [{
        'problem_key': KEY_CERTIFICATES,
        'title': 'mTLS-Zertifikate für QUIC-Mesh in Ordnung bringen',
        'description': f"{problem['reason']}. Ohne gültige Kette läuft der QUIC-Transport nicht im strict-Modus — Peer-Verbindungen bleiben unverschlüsselt oder scheitern.",
        'category': 'system',
        'priority': problem['priority'],
        'source': 'health:certificates',
        'evidence': f"{problem['reason']} | path={certs.get('cert_path', '?')}",
        'steps': problem['steps'],
    }]


def verify_certificates(health: dict[str, Any]) -> tuple[bool, str]:
    problem = certificate_problem(health)
    if problem:
        return True, problem['reason']
    certs = health.get('components', {}).get('certificates', {})
    return False, f"CA + Server vorhanden, Kette gültig, {certs.get('days_left', '?')} Tage Restlaufzeit"
