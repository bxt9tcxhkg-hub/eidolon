from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from eidolon.core.config import state_path
from eidolon.ui.hud_render import apply_runtime_status
from eidolon.ui.hud_support import api_call, write_status
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout


class EidolonHud(QWidget):
    def __init__(self, port: int, status_path: Path):
        super().__init__()
        self.port = port
        self.status_path = status_path
        self.last_error = ''
        self.last_action = ''
        self.setWindowTitle('Eidolon HUD')
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMinimumWidth(360)
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(2500)
        self.refresh()

    def _build_ui(self):
        self.setStyleSheet("""QWidget { background: #11161d; color: #e6edf3; border: 1px solid #30363d; border-radius: 12px; } QLabel { border: none; } QPushButton { background: #1f6feb; color: white; border: none; border-radius: 8px; padding: 8px 10px; } QPushButton#secondary { background: #30363d; }""")
        layout = QVBoxLayout(); layout.setContentsMargins(14, 14, 14, 14); layout.setSpacing(8)
        self.title = QLabel('Eidolon HUD'); self.title.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        self.status = QLabel('Lade Runtime…'); self.workspace = QLabel('Workspace: –'); self.next_action = QLabel('Nächste Aktion: –'); self.mesh = QLabel('Mesh: –'); self.message = QLabel(''); self.message.setWordWrap(True)
        buttons = QHBoxLayout()
        self.execute_btn = QPushButton('Weiter'); self.execute_btn.clicked.connect(self.execute_next)
        self.refresh_btn = QPushButton('Aktualisieren'); self.refresh_btn.setObjectName('secondary'); self.refresh_btn.clicked.connect(self.refresh)
        self.close_btn = QPushButton('Schließen'); self.close_btn.setObjectName('secondary'); self.close_btn.clicked.connect(self.close)
        for button in [self.execute_btn, self.refresh_btn, self.close_btn]: buttons.addWidget(button)
        for widget in [self.title, self.status, self.workspace, self.next_action, self.mesh, self.message]: layout.addWidget(widget)
        layout.addLayout(buttons); self.setLayout(layout)

    def _api(self, method: str, path: str, body: dict | None = None) -> dict: return api_call(self.port, method, path, body)
    def _write_status(self, payload: dict): write_status(self.status_path, payload)

    def refresh(self):
        payload = {'running': True, 'pid': os.getpid(), 'updated_at': datetime.now(timezone.utc).isoformat(), 'available': True, 'last_action': self.last_action, 'last_error': self.last_error}
        try:
            health = self._api('GET', '/health'); autonomy = self._api('GET', '/autonomy/status'); paired = self._api('GET', '/mesh/pairing/paired')
            payload.update(apply_runtime_status(self, health, autonomy, paired)); self.last_error = ''
        except Exception as exc:
            self.last_error = str(exc); self.status.setText('Runtime nicht erreichbar'); self.message.setText(self.last_error); self.execute_btn.setEnabled(False); payload.update({'available': False, 'error': self.last_error})
        self._write_status(payload)

    def execute_next(self):
        try:
            autonomy = self._api('GET', '/autonomy/status'); active = autonomy.get('active_workspace') or {}; workspace_id = active.get('workspace_id')
            if not workspace_id: raise RuntimeError('Kein aktiver Workspace')
            result = self._api('POST', f'/workspaces/{workspace_id}/orchestration/execute', {}); self.last_action = result.get('action') or 'execute'; self.last_error = ''; self.message.setText(f"Ausgeführt: {result.get('action')} ({result.get('module_id')})")
        except Exception as exc:
            self.last_error = str(exc); self.message.setText(f'Ausführung fehlgeschlagen: {exc}')
        self.refresh()

    def closeEvent(self, event):
        self._write_status({'running': False, 'pid': os.getpid(), 'updated_at': datetime.now(timezone.utc).isoformat(), 'available': True, 'last_action': self.last_action, 'last_error': self.last_error})
        return super().closeEvent(event)


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('--port', type=int, default=8002); parser.add_argument('--status-path', default=''); args = parser.parse_args()
    status_path = Path(args.status_path) if args.status_path else state_path('generated', 'ui', 'hud_status.json')
    app = QApplication(sys.argv); hud = EidolonHud(port=args.port, status_path=status_path); hud.resize(420, 220); hud.show(); return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
