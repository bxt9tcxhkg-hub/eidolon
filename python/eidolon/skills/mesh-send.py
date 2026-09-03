"""Mesh-Send-Skill: writes mesh messages to the SQLite inbox."""
from eidolon.mesh.inbox import get_mesh_inbox_store


def run(params: dict) -> dict:
    to = params.get("to", "broadcast")
    message = params.get("message", "")
    msg = get_mesh_inbox_store().append(to=to, message=message, from_id=params.get("from", "host"))
    return {"status": "gesendet", "to": to, "message": message, "timestamp": msg["timestamp"]}
