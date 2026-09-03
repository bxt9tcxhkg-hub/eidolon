from __future__ import annotations

import hashlib
import secrets


class MeshCrypto:
    @staticmethod
    def generate_keypair() -> tuple[str, str]:
        try:
            from nacl.encoding import HexEncoder
            from nacl.signing import SigningKey
            signing_key = SigningKey.generate()
            verify_key = signing_key.verify_key
            return signing_key.encode(encoder=HexEncoder).decode(), verify_key.encode(encoder=HexEncoder).decode()
        except ImportError:
            private = secrets.token_hex(32)
            public = hashlib.sha256(private.encode()).hexdigest()
            return private, public

    @staticmethod
    def sign(private_key: str, message: bytes) -> str:
        try:
            from nacl.encoding import HexEncoder
            from nacl.signing import SigningKey
            signing_key = SigningKey(private_key, encoder=HexEncoder)
            signed = signing_key.sign(message)
            return signed.signature.hex()
        except ImportError:
            return hashlib.sha256(private_key.encode() + message).hexdigest()

    @staticmethod
    def verify(public_key: str, signature: str, message: bytes) -> bool:
        try:
            from nacl.encoding import HexEncoder
            from nacl.signing import SignedMessage, VerifyKey
            verify_key = VerifyKey(public_key, encoder=HexEncoder)
            signed = SignedMessage(signature + message.hex())
            verify_key.verify(signed)
            return True
        except Exception:
            return False
