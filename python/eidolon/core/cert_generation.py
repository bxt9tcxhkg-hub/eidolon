from __future__ import annotations

import datetime
import ipaddress
import socket
from typing import Any


def generate_ca(paths, days: int = 3650, force: bool = False) -> dict[str, Any]:
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.x509.oid import NameOID
    if paths.ca_cert.exists() and not force:
        return {'ok': True, 'skipped': True, 'reason': 'CA existiert bereits'}
    key = ed25519.Ed25519PrivateKey.generate()
    name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'DE'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Eidolon Mesh'),
        x509.NameAttribute(NameOID.COMMON_NAME, 'Eidolon Mesh Root CA'),
    ])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(digital_signature=True, key_cert_sign=True, crl_sign=True, key_encipherment=False, content_commitment=False, data_encipherment=False, key_agreement=False, encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .sign(key, None)
    )
    paths.ca_key.write_bytes(key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
    paths.ca_cert.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return {'ok': True, 'created': True, 'subject': name.rfc4514_string(), 'valid_days': days, 'cert': str(paths.ca_cert)}


def issue_leaf(paths, cn: str, cert_path, key_path, *, server_auth: bool, days: int, extra_sans: list[str] | None = None) -> dict[str, Any]:
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    if not (paths.ca_cert.exists() and paths.ca_key.exists()):
        return {'ok': False, 'error': 'CA fehlt — zuerst generate_ca() aufrufen'}
    ca_cert = x509.load_pem_x509_certificate(paths.ca_cert.read_bytes())
    ca_key = serialization.load_pem_private_key(paths.ca_key.read_bytes(), password=None)
    key = ed25519.Ed25519PrivateKey.generate()
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'DE'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Eidolon Mesh'),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ])
    san_entries: list[Any] = [x509.DNSName('localhost')]
    hostname = socket.gethostname()
    if hostname and hostname != 'localhost':
        san_entries.append(x509.DNSName(hostname))
    for extra in extra_sans or []:
        try:
            san_entries.append(x509.IPAddress(ipaddress.ip_address(extra)))
        except ValueError:
            san_entries.append(x509.DNSName(extra))
    san_entries.append(x509.IPAddress(ipaddress.ip_address('127.0.0.1')))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('8.8.8.8', 80))
        san_entries.append(x509.IPAddress(ipaddress.ip_address(sock.getsockname()[0])))
        sock.close()
    except Exception:
        pass
    seen, sans = set(), []
    for entry in san_entries:
        key_name = str(entry)
        if key_name not in seen:
            seen.add(key_name)
            sans.append(entry)
    eku = [ExtendedKeyUsageOID.SERVER_AUTH] if server_auth else [ExtendedKeyUsageOID.CLIENT_AUTH]
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=5))
        .not_valid_after(now + datetime.timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.SubjectAlternativeName(sans), critical=False)
        .add_extension(x509.ExtendedKeyUsage(eku), critical=False)
        .add_extension(x509.KeyUsage(digital_signature=True, key_encipherment=False, key_cert_sign=False, crl_sign=False, content_commitment=False, data_encipherment=False, key_agreement=False, encipher_only=False, decipher_only=False), critical=True)
        .sign(ca_key, None)
    )
    key_path.write_bytes(key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()))
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return {'ok': True, 'created': True, 'cn': cn, 'sans': [str(item) for item in sans], 'valid_days': days, 'cert': str(cert_path)}
