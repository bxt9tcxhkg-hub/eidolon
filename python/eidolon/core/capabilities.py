from __future__ import annotations

from eidolon.core.capability_catalog import build_default_capabilities
from eidolon.core.capability_models import Capability, CapabilityRegistry


_registry: CapabilityRegistry | None = None


def get_capability_registry() -> CapabilityRegistry:
    global _registry
    if _registry is None:
        _registry = CapabilityRegistry()
        for cap in build_default_capabilities():
            _registry.register(cap)
    return _registry
