from __future__ import annotations

from eidolon.core.settings_schema_autonomy import autonomy_defaults, autonomy_enum_rules, autonomy_float_rules, autonomy_int_rules
from eidolon.core.settings_schema_llm import llm_defaults, llm_enum_rules, llm_float_rules, llm_int_rules
from eidolon.core.settings_schema_mesh import mesh_defaults, mesh_int_rules, proactive_defaults, proactive_enum_rules, proactive_int_rules
from eidolon.core.settings_schema_network import network_defaults, network_enum_rules, network_int_rules
from eidolon.core.settings_schema_surfaces import privacy_defaults, skills_defaults, ui_defaults, ui_enum_rules, workspace_defaults, workspace_enum_rules


def build_default_settings() -> dict[str, dict]:
    return {'network': network_defaults(), 'llm': llm_defaults(), 'autonomy': autonomy_defaults(), 'mesh': mesh_defaults(), 'proactive': proactive_defaults(), 'workspaces': workspace_defaults(), 'skills': skills_defaults(), 'privacy': privacy_defaults(), 'ui': ui_defaults()}


def build_enum_rules() -> dict[tuple[str, str], set[str]]:
    merged = {}
    for chunk in [network_enum_rules(), llm_enum_rules(), autonomy_enum_rules(), proactive_enum_rules(), workspace_enum_rules(), ui_enum_rules()]:
        merged.update(chunk)
    return merged


def build_int_rules() -> dict[tuple[str, str], tuple[int, int]]:
    merged = {}
    for chunk in [network_int_rules(), llm_int_rules(), autonomy_int_rules(), mesh_int_rules(), proactive_int_rules()]:
        merged.update(chunk)
    return merged


def build_float_rules() -> dict[tuple[str, str], tuple[float, float]]:
    merged = {}
    for chunk in [llm_float_rules(), autonomy_float_rules()]:
        merged.update(chunk)
    return merged
