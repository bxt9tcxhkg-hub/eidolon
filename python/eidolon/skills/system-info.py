"""System-Info-Skill: Zeigt System-Informationen an."""
import platform
import psutil
import os

def run(params: dict) -> dict:
    return {
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": dict(psutil.virtual_memory()._asdict()),
        "disk": dict(psutil.disk_usage('/')._asdict()) if hasattr(psutil.disk_usage('/'), '_asdict') else {}
    }
