from __future__ import annotations

from eidolon.operate.store_schema_fragments import SCHEMA_STATEMENTS, ALTER_TABLE_STATEMENTS


def schema_sql() -> str:
    return ' ;\n'.join(statement.strip() for statement in SCHEMA_STATEMENTS) + ';\n'


def migration_sql() -> str:
    return ' ;\n'.join(statement for statement in ALTER_TABLE_STATEMENTS) + ';\n'
