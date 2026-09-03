from __future__ import annotations

from datetime import datetime, timezone
import secrets

from eidolon.core.auth_models import Role, User


def create_user(manager, username, password, role=Role.USER, display_name='', email=''):
    if len(username) < 3:
        return {'ok': False, 'error': 'Username muss mindestens 3 Zeichen lang sein'}
    if len(password) < 8:
        return {'ok': False, 'error': 'Passwort muss mindestens 8 Zeichen lang sein'}
    if manager._store.get_user_by_username(username):
        return {'ok': False, 'error': 'Username bereits vergeben'}
    user = User(
        user_id=secrets.token_urlsafe(16),
        username=username,
        password_hash=manager._hasher.hash_password(password),
        role=role,
        display_name=display_name or username,
        email=email,
    )
    manager._store.create_user(user)
    return {'ok': True, 'user': user.to_dict()}


def authenticate(manager, username, password, ip_address=''):
    rate_key = f'login:{ip_address}'
    if not manager._rate_limiter.is_allowed(rate_key):
        return {'ok': False, 'error': 'Zu viele Login-Versuche'}
    user = manager._store.get_user_by_username(username)
    if not user:
        return {'ok': False, 'error': 'Ungueltige Anmeldedaten'}
    if not user.can_login():
        return {'ok': False, 'error': 'Account ist gesperrt'}
    if not manager._hasher.verify_password(password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= manager._max_login_attempts:
            user.locked_until = (datetime.now(timezone.utc) + manager._lockout_duration).isoformat()
        manager._store.update_user(user)
        return {'ok': False, 'error': 'Ungueltige Anmeldedaten'}
    user.failed_login_attempts = 0
    user.locked_until = ''
    user.last_login_at = datetime.now(timezone.utc).isoformat()
    user.updated_at = user.last_login_at
    manager._store.update_user(user)
    return {'ok': True, 'user': user.to_dict()}


def change_password(manager, user_id, old_password, new_password):
    user = manager._store.get_user(user_id)
    if not user:
        return {'ok': False, 'error': 'User nicht gefunden'}
    if not manager._hasher.verify_password(old_password, user.password_hash):
        return {'ok': False, 'error': 'Altes Passwort ist falsch'}
    if len(new_password) < 8:
        return {'ok': False, 'error': 'Neues Passwort muss mindestens 8 Zeichen lang sein'}
    user.password_hash = manager._hasher.hash_password(new_password)
    user.updated_at = datetime.now(timezone.utc).isoformat()
    manager._store.update_user(user)
    return {'ok': True}
