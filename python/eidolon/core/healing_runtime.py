from __future__ import annotations

from datetime import datetime, timezone

from eidolon.core.healing_checks import healthy, maybe_await


async def run_check_cycle(service) -> dict:
    service._state['total_checks'] += 1
    cycle = {'checked_at': datetime.now(timezone.utc).isoformat(), 'checks': {}}
    for name, fn in service._checks.items():
        try:
            result = await maybe_await(fn())
            ok = healthy(result)
            cycle['checks'][name] = {'ok': ok, 'result': result}
            if ok:
                service._state['consec_success'][name] = int(service._state['consec_success'].get(name, 0)) + 1
            else:
                service._state['consec_success'][name] = 0
                service._state['error_counts'][name] = int(service._state['error_counts'].get(name, 0)) + 1
        except Exception as exc:
            cycle['checks'][name] = {'ok': False, 'error': str(exc)}
            service._state['consec_success'][name] = 0
            service._state['error_counts'][name] = int(service._state['error_counts'].get(name, 0)) + 1
    service._append_log(cycle)
    return cycle


async def attempt_targeted_recovery(service, check_name: str) -> dict:
    try:
        if check_name == 'certificates':
            from eidolon.mesh.crypto.certstore import ensure_self_signed
            cert, key = ensure_self_signed()
            service._state['total_recoveries'] += 1
            return {'ok': True, 'strategy': 'ensure_self_signed', 'cert': cert, 'key': key}
        if check_name == 'skills':
            service._state['total_recoveries'] += 1
            return {'ok': True, 'strategy': 'skill_reload_requested'}
        if check_name in service._restart_hooks:
            result = await maybe_await(service._restart_hooks[check_name]())
            service._state['total_recoveries'] += 1
            return {'ok': True, 'strategy': 'restart_hook', 'result': result}
        if check_name in service._checks:
            result = await maybe_await(service._checks[check_name]())
            ok = healthy(result)
            if ok:
                service._state['total_recoveries'] += 1
            return {'ok': ok, 'strategy': 'recheck', 'result': result}
        return {'ok': False, 'strategy': 'no_strategy', 'detail': check_name}
    except Exception as exc:
        return {'ok': False, 'strategy': 'exception', 'error': str(exc)}
