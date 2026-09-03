from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def register_browser_device_pairing(pairing, code: str, *, device_name: str, peer_id: str, public_key: str, address: str, user_agent: str = '') -> dict[str, Any]:
    request = pairing.get_request(code)
    if not request:
        return {'ok': False, 'error': 'Code ungültig oder abgelaufen'}
    import time
    if time.time() > request.expires_at:
        return {'ok': False, 'error': 'Code ungültig oder abgelaufen'}
    clean_peer_id = (peer_id or '').strip()
    clean_public_key = (public_key or '').strip()
    clean_name = (device_name or '').strip()[:80] or 'Gekoppeltes Gerät'
    if not clean_peer_id or not clean_public_key:
        return {'ok': False, 'error': 'Geräteidentität fehlt'}
    pairing._paired[clean_peer_id] = {
        'name': clean_name,
        'address': address,
        'port': 0,
        'public_key': clean_public_key,
        'kind': 'browser_device',
        'user_agent': user_agent[:200],
        'paired_at': datetime.now(tz=timezone.utc).isoformat(),
    }
    request.status = 'accepted'
    pairing._requests.pop(code, None)
    pairing._save()
    return {'ok': True, 'peer_id': clean_peer_id, 'peer': pairing._paired[clean_peer_id]}


def generate_qr_svg(payload: str) -> str:
    try:
        import io
        import qrcode
        import qrcode.image.svg
        factory = qrcode.image.svg.SvgPathImage
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2, image_factory=factory)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image()
        buf = io.BytesIO()
        img.save(buf)
        svg = buf.getvalue().decode('utf-8')
        if svg.startswith('<?xml'):
            svg = svg.split('?>', 1)[1].lstrip()
        return svg.replace('<svg ', '<svg style="background:#fff;border-radius:6px;width:200px;height:200px;display:block;" ', 1)
    except Exception as exc:
        return f'<div style="padding:16px;color:#dc2626;font-size:0.8rem;">QR-Generierung fehlgeschlagen: {exc}</div>'


def generate_qr_png_data_url(payload: str) -> str:
    try:
        import base64
        import io
        import qrcode
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"
    except Exception:
        return ''


def qr_debug_info(payload: str) -> dict[str, Any]:
    info: dict[str, Any] = {'payload_chars': len(payload), 'library': None}
    try:
        import qrcode
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
        qr.add_data(payload)
        qr.make(fit=True)
        info.update({'library': 'qrcode', 'version': qr.version, 'modules': qr.modules_count, 'error_correction': 'M (15%)', 'scannable': True})
    except Exception as exc:
        info['error'] = str(exc)
        info['scannable'] = False
    return info
