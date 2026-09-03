from __future__ import annotations


def apply_runtime_status(hud, health: dict, autonomy: dict, paired: dict):
    active = autonomy.get('active_workspace') or {}
    orchestration = active.get('orchestration') or {}
    next_best = orchestration.get('next_best_action') or {}
    hud.status.setText(f"Runtime: {health.get('status', 'unbekannt')} · QUIC: {(health.get('components', {}).get('quic_port', {}) or {}).get('status', '–')}")
    hud.workspace.setText(f"Workspace: {active.get('topic_label', 'kein aktiver Workspace')}")
    hud.next_action.setText(f"Nächste Aktion: {next_best.get('label') or next_best.get('action') or '–'}")
    hud.mesh.setText(f"Mesh: {len(paired.get('paired', []))} gekoppelte Peers")
    hud.message.setText(f"Letzter Fehler: {hud.last_error}" if hud.last_error else "Direkte Steuerung: 'Weiter' führt die nächste echte Workspace-Aktion aus.")
    hud.execute_btn.setEnabled(bool(active.get('workspace_id')) and bool(next_best.get('action')))
    return {'health': health.get('status'), 'quic': (health.get('components', {}).get('quic_port', {}) or {}).get('status'), 'active_workspace': active.get('workspace_id'), 'active_workspace_label': active.get('topic_label'), 'next_action': next_best.get('label') or next_best.get('action'), 'paired_peers': len(paired.get('paired', []))}
