from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Any
import json
import logging

from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
import datetime as dt


logger = logging.getLogger("eidolon.mesh.crypto")


class MeshCrypto:
    def __init__(self, cert_path: Path, key_path: Path) -> None:
        self.cert_path = cert_path
        self.key_path = key_path
        self._private_key = ed25519.Ed25519PrivateKey.generate()
        self._public_key = self._private_key.public_key()

    def sign(self, data: bytes) -> bytes:
        return self._private_key.sign(data)

    def verify(self, public_key: ed25519.Ed25519PublicKey, data: bytes, signature: bytes) -> bool:
        try:
            public_key.verify(signature, data)
            return True
        except Exception:
            return False

    def public_key_pem(self) -> bytes:
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def self_signed_cert(self, common_name: str, valid_days: int = 3650) -> tuple[x509.Certificate, ed25519.Ed25519PrivateKey]:
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        subject = issuer = x509.Name([
            x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, common_name),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(dt.timezone.utc))
            .not_valid_after(datetime.datetime.now(dt.timezone.utc) + datetime.timedelta(days=valid_days))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(private_key, hashes.SHA256())
        )
        return cert, private_key

    def save_cert_key(self, cert: x509.Certificate, private_key: ed25519.Ed25519PrivateKey) -> None:
        self.cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
        self.key_path.write_bytes(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))
