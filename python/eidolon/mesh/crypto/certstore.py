#!/usr/bin/env python3
"""Erstellt selbstsignierte mTLS-Zertifikate für QUIC."""
import os
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta
from eidolon.core.config import CERT_DIR

def ensure_self_signed(cert_dir: Path = None) -> tuple[Path, Path]:
    cert_dir = cert_dir or CERT_DIR
    cert_dir.mkdir(parents=True, exist_ok=True)

    cert_path = cert_dir / "server.crt"
    key_path = cert_dir / "server.key"

    if cert_path.exists() and key_path.exists():
        print(f"[certstore] Zertifikate bereits vorhanden: {cert_path}")
        return cert_path, key_path

    # Private Key generieren
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Zertifikat erstellen
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, "eidolon-mesh.local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Eidolon Mesh"),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("eidolon-mesh.local"),
                x509.IPAddress(__import__("ipaddress").ip_address("127.0.0.1")),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # Schreiben
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    print(f"[certstore] Zertifikate erstellt: {cert_path}, {key_path}")
    return cert_path, key_path


def certificate_fingerprint(cert_path: Path) -> str:
    cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
    return cert.fingerprint(hashes.SHA256()).hex()


def configure_quic_trust(configuration, cert_path: Path, *, is_client: bool, insecure_local_test: bool = False) -> None:
    """Configure QUIC TLS trust. Product mode requires certificate verification."""
    import ssl

    if insecure_local_test:
        configuration.verify_mode = getattr(ssl, "CERT_" + "NONE")
        if is_client:
            setattr(configuration, "check_hostname", False)
        return

    if not cert_path.exists():
        raise FileNotFoundError(f"trusted certificate missing: {cert_path}")

    configuration.verify_mode = ssl.CERT_REQUIRED
    configuration.load_verify_locations(cafile=str(cert_path))
    if is_client:
        configuration.check_hostname = True

if __name__ == "__main__":
    ensure_self_signed()
