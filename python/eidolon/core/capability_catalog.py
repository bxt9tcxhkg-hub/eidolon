from __future__ import annotations

from eidolon.core.capability_checks import browser_control_available, cmd_available, hud_runtime_available, image_generation_available, mesh_quic_available, module_available, ollama_available
from eidolon.core.capability_models import Capability


def build_default_capabilities() -> list[Capability]:
    return [
        Capability('file.read', 'Dateien lesen', inputs={'path': 'str'}, outputs={'content': 'str'}),
        Capability('file.write', 'Dateien schreiben', inputs={'path': 'str', 'content': 'str'}, outputs={'ok': 'bool'}),
        Capability('python.execute', 'Python lokal ausführen', inputs={'code': 'str'}, outputs={'stdout': 'str'}, _check_fn=lambda: cmd_available('python')),
        Capability('browser.control', 'Browser steuern', provider='web', _check_fn=browser_control_available, detail='Playwright/Chromium-Steuerung verfügbar, wenn Playwright installiert ist'),
        Capability('image.generate', 'Bildgenerierung', provider='local', _check_fn=image_generation_available, detail='Lokale Text-to-Image-Pipeline verfügbar, wenn diffusers und ein Modell vorhanden sind'),
        Capability('tts.speak', 'Text-to-Speech', provider='local', _check_fn=lambda: module_available('pyttsx3') or cmd_available('edge-tts')),
        Capability('mesh.quic', 'QUIC/mTLS Transport', provider='mesh', _check_fn=mesh_quic_available),
        Capability('ui.hud', 'Desktop HUD / Overlay', provider='ui', _check_fn=hud_runtime_available, detail='Produktiver HUD-Pfad vorhanden, solange Status-/Start-Endpunkte erreichbar sind'),
        Capability('llm.ollama', 'Lokales Ollama LLM', provider='ollama', _check_fn=ollama_available),
        Capability('evidence.store', 'SQLite Evidence Store', provider='sqlite', _check_fn=lambda: True),
        Capability('skills.runtime', 'Skill Runtime', provider='local', _check_fn=lambda: True),
        Capability('autonomy.loop', 'Autonomy background loop', provider='local', _check_fn=lambda: True),
    ]
