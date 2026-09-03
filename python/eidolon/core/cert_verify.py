from __future__ import annotations

import datetime
from typing import Any

from eidolon.core.cert_status import is_ca


def verify_chain(paths) -> dict[str, Any]:
    from cryptography import x509
    from cryptography.exceptions import InvalidSignature
    if not (paths.ca_cert.exists() and paths.server_cert.exists()):
        return {'ok': False, 'error': 'CA oder Server-Zertifikat fehlt'}
    ca = x509.load_pem_x509_certificate(paths.ca_cert.read_bytes())
    srv = x509.load_pem_x509_certificate(paths.server_cert.read_bytes())
    checks: dict[str, Any] = {
        'issuer_matches_ca_subject': srv.issuer == ca.subject,
        'ca_is_ca': is_ca(ca),
        'server_is_not_ca': not is_ca(srv),
    }
    try:
        ca.public_key().verify(srv.signature, srv.tbs_certificate_bytes)
        checks['signature_valid'] = True
    except InvalidSignature:
        checks['signature_valid'] = False
    except Exception as exc:
        checks['signature_valid'] = False
        checks['signature_error'] = str(exc)
    now = datetime.datetime.now(datetime.timezone.utc)
    checks['server_in_validity_window'] = srv.not_valid_before_utc <= now <= srv.not_valid_after_utc
    checks['ca_in_validity_window'] = ca.not_valid_before_utc <= now <= ca.not_valid_after_utc
    return {'ok': all(bool(value) for key, value in checks.items() if not key.endswith('_error')), 'checks': checks}
