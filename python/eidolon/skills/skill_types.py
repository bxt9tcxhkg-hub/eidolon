from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Skill:
    name: str
    handler: str
    params: list[str]
    fn: Callable[[dict[str, Any]], dict[str, Any]]
    enabled: bool = True
    priority: int = 0
    description: str = ''

    def to_dict(self) -> dict[str, Any]:
        return {'name': self.name, 'handler': self.handler, 'params': self.params, 'enabled': self.enabled, 'priority': self.priority, 'description': self.description}
