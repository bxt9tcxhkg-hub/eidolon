from __future__ import annotations

from eidolon.core.settings_schema_builders import build_default_settings, build_enum_rules, build_float_rules, build_int_rules


ENUM_RULES = build_enum_rules()
INT_RANGE_RULES = build_int_rules()
FLOAT_RANGE_RULES = build_float_rules()
DEFAULT_SETTINGS = build_default_settings()
