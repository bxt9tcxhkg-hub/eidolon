from __future__ import annotations

from pathlib import Path

from eidolon.bots.role_registry_ops import create_role, delete_role, registry_summary, update_role
from eidolon.bots.role_registry_store import bootstrap_defaults, ensure_default_templates, load_registry, save_registry
from eidolon.core.config import state_path


class BotRoleRegistry:
    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.path = state_path('user', 'bot_roles.json', project_root=self.project_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def snapshot(self) -> dict:
        data = load_registry(self.path)
        if not self.path.exists():
            save_registry(self.path, data)
        if not data.get('roles'):
            bootstrap_defaults(self.path)
            data = load_registry(self.path)
        return ensure_default_templates(self.path, data)

    def summary(self) -> dict:
        return registry_summary(self.list_roles())

    def list_roles(self) -> list[dict]:
        return self.snapshot().get('roles', [])

    def get_role(self, role_id: str) -> dict | None:
        for role in self.snapshot().get('roles', []):
            if role.get('role_id') == role_id:
                return role
        return None

    def create_role(self, payload: dict) -> dict:
        data = self.snapshot()
        created = create_role(data, payload)
        save_registry(self.path, data)
        return created

    def update_role(self, role_id: str, payload: dict) -> dict:
        data = self.snapshot()
        updated = update_role(data, role_id, payload)
        save_registry(self.path, data)
        return updated

    def delete_role(self, role_id: str) -> dict:
        data = self.snapshot()
        removed = delete_role(data, role_id)
        save_registry(self.path, data)
        return removed


_registry: BotRoleRegistry | None = None


def get_bot_role_registry(project_root: str | Path) -> BotRoleRegistry:
    global _registry
    if _registry is None:
        _registry = BotRoleRegistry(project_root)
    return _registry
