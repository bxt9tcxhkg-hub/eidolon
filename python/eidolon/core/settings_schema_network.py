from __future__ import annotations

from typing import Any

from eidolon.core.config import HTTP_PORT, MESH_DISCOVERY_PORT, OLLAMA_URL, QUIC_PORT


def network_defaults() -> dict[str, Any]:
    return {'http_port': HTTP_PORT, 'quic_port': QUIC_PORT, 'mesh_discovery_port': MESH_DISCOVERY_PORT, 'quic_mode': 'strict', 'auto_discovery': True, 'udp_scope': 'subnet'}


def network_enum_rules() -> dict[tuple[str, str], set[str]]:
    return {('network', 'quic_mode'): {'strict', 'local_test'}, ('network', 'udp_scope'): {'local', 'subnet'}}


def network_int_rules() -> dict[tuple[str, str], tuple[int, int]]:
    return {('network', 'http_port'): (1, 65535), ('network', 'quic_port'): (1, 65535), ('network', 'mesh_discovery_port'): (1, 65535)}
