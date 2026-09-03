"""Device status skill backed by the SQLite mesh inbox."""
import json

from eidolon.core.config import state_path
from eidolon.mesh.inbox import get_mesh_inbox_store


def run(params: dict) -> dict:
    devices_path = state_path('mesh', 'devices.json')

    devices = []
    if devices_path.exists():
        devices = json.loads(devices_path.read_text())

    inbox = get_mesh_inbox_store().list(limit=1000)

    return {
        "connected_devices": len(devices),
        "devices": devices,
        "pending_messages": len([m for m in inbox if m.get("to") == "broadcast" or not m.get("delivered")]),
        "inbox_total": len(inbox),
    }
