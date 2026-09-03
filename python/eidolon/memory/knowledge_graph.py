"""Funktionale Wrapper-API für den Knowledge Graph.

Dies ist ein **Thin Wrapper** um ``KnowledgeGraph`` aus ``eidolon.memory.graph``.
Alle Logik existiert in genau einer Implementierung (``graph.py``).
Diese Datei existiert nur für Rückwärtskompatibilität mit Code,
der die funktionale API (``init_db``, ``query_entity``, ``store_intent``) nutzt.
"""
from __future__ import annotations

from eidolon.core.config import GRAPH_DB
from eidolon.memory.graph import KnowledgeGraph

# Singleton-Instanz für die funktionale API
_default_instance: KnowledgeGraph | None = None


def _get_default() -> KnowledgeGraph:
    global _default_instance
    if _default_instance is None:
        _default_instance = KnowledgeGraph(GRAPH_DB)
    return _default_instance


def init_db() -> None:
    """Initialisiert das Datenbankschema (no-op, da _init_schema im Konstruktor läuft)."""
    _get_default()


def _get_conn():
    """Kompatibilitätsfunktion — gibt eine rohe sqlite3-Verbindung zurück."""
    import sqlite3
    conn = sqlite3.connect(str(GRAPH_DB))
    conn.row_factory = sqlite3.Row
    return conn


def insert_entity(entity_type: str, name: str, content: str = "", metadata: dict | None = None) -> int:
    """Fügt eine Entity hinzu oder aktualisiert sie (Upsert). Gibt entity_id zurück."""
    kg = _get_default()
    # Generate a deterministic ID from name+type
    import hashlib
    entity_id = f"ent_{hashlib.md5(f'{entity_type}:{name}'.encode()).hexdigest()[:12]}"
    properties = {"content": content}
    if metadata:
        properties.update(metadata)
    kg.add_entity(entity_id, entity_type, name, properties)
    # Return a numeric ID (best-effort)
    row = _get_conn().execute(
        "SELECT id FROM entities WHERE entity_type=? AND name=?", (entity_type, name)
    ).fetchone()
    return row[0] if row else 0


def query_entity(name: str | None = None, entity_type: str | None = None, limit: int = 50):
    """Fragt Entities mit optionalen Filtern ab."""
    return _get_default().query_entity(name=name, entity_type=entity_type, limit=limit)


def query_relationships(entity_id: int | None = None, rel_type: str | None = None, limit: int = 100):
    """Fragt Relationships ab."""
    return _get_default().query_relationships(entity_id=entity_id, rel_type=rel_type, limit=limit)


def store_intent(intent_id: str, name: str, confidence: float, params: dict, skill_id: str | None = None):
    """Speichert erkannte Intents als Entities im Knowledge-Graph."""
    return _get_default().store_intent(intent_id, name, confidence, params, skill_id)


def get_stats():
    """Gibt Statistiken über den Knowledge-Graph zurück."""
    return _get_default().get_stats()
