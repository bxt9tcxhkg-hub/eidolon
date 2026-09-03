from __future__ import annotations

from pathlib import Path

from eidolon.core.config import QUIC_INSECURE_LOCAL_TEST
from eidolon.mesh.crypto.certstore import configure_quic_trust, ensure_self_signed


def server_configuration(cert_dir: Path):
    from aioquic.quic.configuration import QuicConfiguration
    cert_path, key_path = ensure_self_signed(cert_dir)
    trust_anchor = cert_dir / 'ca.crt'
    if not trust_anchor.exists():
        trust_anchor = cert_path
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(str(cert_path), str(key_path))
    configure_quic_trust(configuration, trust_anchor, is_client=False, insecure_local_test=QUIC_INSECURE_LOCAL_TEST)
    return configuration


def client_configuration(cert_dir: Path):
    from aioquic.quic.configuration import QuicConfiguration
    cert_path, key_path = ensure_self_signed(cert_dir)
    client_cert_path = cert_dir / 'client.crt'
    client_key_path = cert_dir / 'client.key'
    if not client_cert_path.exists():
        client_cert_path = cert_path
    if not client_key_path.exists():
        client_key_path = key_path
    trust_anchor = cert_dir / 'ca.crt'
    if not trust_anchor.exists():
        trust_anchor = cert_path
    configuration = QuicConfiguration(is_client=True)
    configuration.load_cert_chain(str(client_cert_path), str(client_key_path))
    configure_quic_trust(configuration, trust_anchor, is_client=True, insecure_local_test=QUIC_INSECURE_LOCAL_TEST)
    return configuration
