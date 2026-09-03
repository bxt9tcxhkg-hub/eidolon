from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any


def is_ca(cert) -> bool:
    from cryptography import x509
    try:
        basic = cert.extensions.get_extension_for_class(x509.BasicConstraints)
        return bool(basic.value.ca)
    except x509.ExtensionNotFound:
        return False


def inspect_certificate(path: Path) -> dict[str, Any]:
    from cryptography import x509
    cert = x509.load_pem_x509_certificate(path.read_bytes())
    not_after = cert.not_valid_after_utc
    days_left = (not_after - datetime.datetime.now(datetime.timezone.utc)).days
    sans: list[str] = []
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        sans = [str(value.value) for value in ext.value]
    except x509.ExtensionNotFound:
        pass
    return {
        'subject': cert.subject.rfc4514_string(),
        'issuer': cert.issuer.rfc4514_string(),
        'serial': str(cert.serial_number),
        'not_before': cert.not_valid_before_utc.isoformat(),
        'not_after': not_after.isoformat(),
        'days_left': days_left,
        'sans': sans,
        'is_ca': is_ca(cert),
    }


def build_status(paths) -> dict[str, Any]:
    out: dict[str, Any] = {
        'ca_exists': paths.ca_cert.exists() and paths.ca_key.exists(),
        'server_exists': paths.server_cert.exists() and paths.server_key.exists(),
        'client_exists': paths.client_cert.exists() and paths.client_key.exists(),
        'dir': str(paths.dir),
    }
    out['complete'] = out['ca_exists'] and out['server_exists']
    if out['server_exists']:
        try:
            info = inspect_certificate(paths.server_cert)
            out['server_subject'] = info['subject']
            out['server_issuer'] = info['issuer']
            out['server_not_after'] = info['not_after']
            out['server_days_left'] = info['days_left']
            out['server_sans'] = info['sans']
            out['server_expired'] = info['days_left'] < 0
        except Exception as exc:
            out['server_error'] = str(exc)
    return out
