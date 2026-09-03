from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from eidolon.workspaces.domain_rules import VALID_TRANSITIONS
from eidolon.workspaces.domain_time import now_iso


@dataclass
class Task:
    id: str
    title: str
    description: str = ''
    status: str = 'backlog'
    priority: int = 0
    domain: str = 'project'
    owner: str = ''
    notes: str = ''
    blocker_reason: str = ''
    dependencies: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    due_at: str = ''
    completed_at: str = ''
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def can_transition_to(self, new_status: str) -> bool:
        allowed = VALID_TRANSITIONS.get(self.domain, VALID_TRANSITIONS['project']).get(self.status, [])
        return new_status in allowed

    def transition(self, new_status: str) -> dict[str, Any]:
        if not self.can_transition_to(new_status):
            return {
                'ok': False,
                'error': f"Übergang von '{self.status}' zu '{new_status}' ist nicht erlaubt",
                'allowed': VALID_TRANSITIONS.get(self.domain, {}).get(self.status, []),
            }
        old_status = self.status
        self.status = new_status
        self.updated_at = now_iso()
        if new_status == 'done':
            self.completed_at = self.updated_at
            self.blocker_reason = ''
        elif new_status in ('backlog', 'ready', 'todo'):
            self.completed_at = ''
        return {'ok': True, 'id': self.id, 'from': old_status, 'to': new_status, 'updated_at': self.updated_at}

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'domain': self.domain,
            'owner': self.owner,
            'notes': self.notes,
            'blocker_reason': self.blocker_reason,
            'dependencies': self.dependencies,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'due_at': self.due_at,
            'completed_at': self.completed_at,
            'tags': self.tags,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'Task':
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            status=data.get('status', 'backlog'),
            priority=data.get('priority', 0),
            domain=data.get('domain', 'project'),
            owner=data.get('owner', ''),
            notes=data.get('notes', ''),
            blocker_reason=data.get('blocker_reason', ''),
            dependencies=data.get('dependencies', []),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', ''),
            due_at=data.get('due_at', ''),
            completed_at=data.get('completed_at', ''),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
        )
