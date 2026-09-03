# Eidolon v2 — Architekturplanung

**Datum:** 2026-08-17  
**Status:** Planung abgeschlossen, Implementierung startet jetzt

## Design-Prinzipien
1. **Keine Drittanbieter-Kanäle** — nur eigenes Mesh: QUIC, WebRTC, mDNS, BLE, Thread/Matter
2. **Keine Cloud-Abhängigkeit** — alle LLMs lokal, keine API-Kosten
3. **Geräte-Souveränität** — jedes Gerät ist gleichberechtigt, kein zentraler Server notwendig
4. **Intentionsverständnis** statt Befehlsausführung
5. **Stufe 3** — System-Designer mit Selbstheilung, Explainability, Meta-Lernen
6. **Rust+Python-Hybrid** — Rust für Runtime/Sicherheit/Mesh, Python für Skills/LLM

## Architektur

### 1. Intent Layer
- Nutzerabsicht verstehen, nicht nur Keywords matchen
- LLM-gestützte Intent-Erkennung mit lokalem Modell
- Parameter-Extraktion aus natürlicher Sprache
- Skill-Auswahl basierend auf Intent, nicht auf Text-Matching

### 2. Skill Engine
- Dynamische Skills, nicht feste JSON-Dateien
- Skills können Python-Funktionen oder externe Prozesse aufrufen
- Skills sind versioniert und signiert
- Skills können sich gegenseitig aufrufen

### 3. Mesh Layer (direkt, ohne Server)
- QUIC/mTLS für Hauptkommunikation
- mDNS/BLE für Discovery
- Device-Pairing via 6-stelligen Code + Zertifikat
- Offline-First: Geräte arbeiten auch ohne Netzwerk
- Sync-Protokoll für Konfliktauflösung

### 4. Memory Layer
- Graph-basiertes episodisches Memory
- Semantic Search über lokale Embeddings
- Kein Context-Bloat, dynamische Zusammenfassung
- Proaktives Erinnern basierend auf Kontext

### 5. Security Layer
- Zero-Trust: jedes Gerät muss sich authentifizieren
- mTLS-Zertifikate für alle Geräte
- Lokale Credentials, nie in der Cloud
- Sandbox für Skills

### 6. LLM Layer
- Lokal via Ollama, kein Cloud-LLM
- Model-Routing: kleines Modell für Simple Tasks, großes für komplexe
- Prompt-Caching für Performance
- Offline-Modus mit lokalen Fallbacks

## Projektstruktur v2

```
eidolon/
├── Cargo.toml (Rust Workspace)
├── crates/
│   ├── eidolon-runtime/     # Rust Core, Event Loop, Scheduling
│   ├── eidolon-mesh/        # QUIC, mDNS, BLE, Discovery
│   ├── eidolon-security/    # mTLS, Zero-Trust, Sandbox
│   ├── eidolon-memory/      # Graph Memory, Semantic Search
│   └── eidolon-skills/      # Skill Runtime, Isolation
├── python/
│   ├── eidolon/
│   │   ├── skills/          # Python Skills
│   │   ├── llm/             # Ollama Integration
│   │   └── ui/              # Web UI, Desktop Overlay
│   └── agent_server.py      # Python API Gateway
└── docs/
    └── ARCHITECTURE.md
```

## Implementierungsreihenfolge

1. **Intent Engine** — LLM-gestützte Intent-Erkennung
2. **Skill Runtime** — dynamische Skills mit Python
3. **Mesh Discovery** — mDNS + QUIC ohne Server
4. **Memory Graph** — episodisches Memory
5. **Security** — mTLS + Zero-Trust
6. **Rust Migration** — sobald Toolchain verfügbar

## Nächster Schritt

Ich starte jetzt mit **1. Intent Engine** — baue ein Intent-System, das natürliche Sprache versteht und Skills basierend darauf auswählt.
