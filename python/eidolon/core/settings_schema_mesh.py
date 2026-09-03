from __future__ import annotations

from typing import Any


def mesh_defaults() -> dict[str, Any]:
    return {'pairing_ttl_seconds': 300, 'auto_accept_known': False, 'auto_prune_offline_days': 30, 'heartbeat_interval_s': 120, 'max_peers': 20, 'trusted_fingerprints': []}


def mesh_int_rules() -> dict[tuple[str, str], tuple[int, int]]:
    return {('mesh', 'pairing_ttl_seconds'): (1, 86400), ('mesh', 'auto_prune_offline_days'): (0, 3650), ('mesh', 'heartbeat_interval_s'): (1, 86400), ('mesh', 'max_peers'): (1, 10000)}


def proactive_defaults() -> dict[str, Any]:
    return {'enabled': True, 'assistance_mode': 'offer', 'max_visible': 3, 'cooldown_new_s': 3600, 'cooldown_dismissed_s': 7200, 'cooldown_unhelpful_s': 14400, 'cooldown_ignored_s': 1800, 'ignored_topics': [], 'suggestion_style': 'card'}


def proactive_enum_rules() -> dict[tuple[str, str], set[str]]:
    return {('proactive', 'assistance_mode'): {'prepare', 'offer', 'execute'}, ('proactive', 'suggestion_style'): {'text', 'card', 'inline'}}


def proactive_int_rules() -> dict[tuple[str, str], tuple[int, int]]:
    return {('proactive', 'max_visible'): (0, 20), ('proactive', 'cooldown_new_s'): (0, 604800), ('proactive', 'cooldown_dismissed_s'): (0, 604800), ('proactive', 'cooldown_unhelpful_s'): (0, 604800), ('proactive', 'cooldown_ignored_s'): (0, 604800)}
