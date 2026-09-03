from __future__ import annotations

import hashlib
import hmac
import secrets


class PasswordHasher:
    def __init__(self):
        self._bcrypt = None
        try:
            import bcrypt
            self._bcrypt = bcrypt
        except ImportError:
            pass

    def hash_password(self, password, /):
        if self._bcrypt:
            salt = self._bcrypt.gensalt()
            return self._bcrypt.hashpw(password.encode(), salt).decode()
        salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f'pbkdf2:{salt}:{key.hex()}'

    def verify_password(self, password, hashed, /):
        if not hashed:
            return False
        if self._bcrypt:
            try:
                return self._bcrypt.checkpw(password.encode(), hashed.encode())
            except Exception:
                return False
        if hashed.startswith('pbkdf2:'):
            parts = hashed.split(':', 2)
            if len(parts) != 3:
                return False
            _, salt, key_hex = parts
            key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hmac.compare_digest(key.hex(), key_hex)
        return False
