#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request


def get_json(base: str, path: str, timeout: int = 120):
    with urllib.request.urlopen(base + path, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode('utf-8'))


def post_json(base: str, path: str, payload: dict, timeout: int = 600):
    request = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, json.loads(response.read().decode('utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8002')
    parser.add_argument('--loops', type=int, default=3)
    args = parser.parse_args()

    base = args.base_url.rstrip('/')
    report: dict[str, object] = {'base_url': base, 'checks': {}}

    for path in ['/health', '/autonomy/status', '/evidence/summary', '/runtime/process', '/voice/status', '/browser/sessions']:
        status, body = get_json(base, path)
        report['checks'][path] = {'status': status, 'ok': body.get('ok'), 'keys': sorted(body.keys())[:10]}

    status, auto = get_json(base, '/autonomy/status')
    active_workspace = auto.get('active_workspace') or {}
    if active_workspace.get('workspace_id'):
        status, body = post_json(base, f"/workspaces/{active_workspace['workspace_id']}/orchestration/execute", {})
        report['checks']['workspace_execute'] = {
            'status': status,
            'ok': body.get('ok'),
            'selection_reason': body.get('selection_reason'),
            'evidence': body.get('evidence'),
        }

    status, speak = post_json(base, '/voice/speak', {'text': 'Eidolon runtime truth verification'})
    report['checks']['voice_speak'] = {
        'status': status,
        'ok': speak.get('ok'),
        'path': speak.get('path'),
        'size_bytes': speak.get('size_bytes'),
    }
    if speak.get('path'):
        status, transcribe = post_json(base, '/voice/transcribe', {'audio_path': speak['path']})
        report['checks']['voice_transcribe'] = {
            'status': status,
            'ok': transcribe.get('ok'),
            'blocked': transcribe.get('blocked'),
            'error': transcribe.get('error'),
        }

    status, created = post_json(base, '/browser/sessions', {'url': 'https://example.com', 'headless': True})
    report['checks']['browser_create'] = {'status': status, 'ok': created.get('ok'), 'session_id': created.get('session_id')}
    session_id = created.get('session_id')
    if session_id:
        status, extracted = post_json(base, f'/browser/sessions/{session_id}/extract', {'selector': 'h1'})
        report['checks']['browser_extract'] = {'status': status, 'ok': extracted.get('ok'), 'text': extracted.get('text')}
        status, screenshot = post_json(base, f'/browser/sessions/{session_id}/screenshot', {})
        report['checks']['browser_screenshot'] = {'status': status, 'ok': screenshot.get('ok'), 'path': screenshot.get('path')}
        req = urllib.request.Request(base + f'/browser/sessions/{session_id}', method='DELETE')
        with urllib.request.urlopen(req, timeout=120) as response:
            deleted = json.loads(response.read().decode('utf-8'))
        report['checks']['browser_delete'] = {'status': response.status, 'ok': deleted.get('ok')}

    status, image = post_json(base, '/image/generate', {'prompt': 'A dark terminal-first agent UI, realistic product screenshot'})
    report['checks']['image_generate'] = {'status': status, 'ok': image.get('ok'), 'path': image.get('path')}

    loop_results = []
    for i in range(args.loops):
        for path in ['/health', '/autonomy/status', '/runtime/process']:
            status, body = get_json(base, path)
            loop_results.append({'iteration': i, 'path': path, 'status': status, 'ok': body.get('ok')})
        time.sleep(0.2)
    report['checks']['loops'] = loop_results

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
