"""System-Info-Skill: Zeigt System-Informationen an."""
import platform

def run(params: dict) -> dict:
    payload = {
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
    }
    try:
        import psutil
        interval = 0.1
        if isinstance(params, dict) and params.get('interval') is not None:
            interval = float(params.get('interval'))
        payload['cpu_percent'] = psutil.cpu_percent(interval=max(0.0, interval))
        payload['memory'] = dict(psutil.virtual_memory()._asdict())
        usage = psutil.disk_usage('/')
        payload['disk'] = dict(usage._asdict()) if hasattr(usage, '_asdict') else {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
        }
    except Exception as exc:
        payload['psutil'] = f'nicht verfügbar: {exc}'
    return payload
