from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ProjectElement:
    id: str
    title: str
    description: str = ''
    status: str = 'idea'
    priority: int = 0
    element_type: str = 'task'
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    parent_id: str | None = None
    assigned_to: str = ''
    due_at: str = ''
    completed_at: str = ''
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    domain: str = ''
    domain_data: dict = field(default_factory=dict)
    position: dict = field(default_factory=lambda: {'x': 0, 'y': 0})
    sort_order: int = 0

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'element_type': self.element_type,
            'tags': self.tags,
            'dependencies': self.dependencies,
            'assigned_to': self.assigned_to,
            'due_at': self.due_at,
            'completed_at': self.completed_at,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'domain': self.domain,
            'domain_data': self.domain_data,
            'position': self.position,
            'parent_id': self.parent_id,
            'sort_order': self.sort_order,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ProjectElement':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Project:
    id: str
    title: str
    description: str = ''
    status: str = 'active'
    domain: str = ''
    elements: list[ProjectElement] = field(default_factory=list)
    inbox: list[dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'domain': self.domain,
            'elements': [element.to_dict() for element in self.elements],
            'inbox': self.inbox,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Project':
        data['elements'] = [ProjectElement.from_dict(item) for item in data.get('elements', [])]
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
