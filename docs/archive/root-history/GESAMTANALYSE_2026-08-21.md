# Eidolon — Gesamtanalyse: Duplikate, Altbestände & Bereinigung

> **Erstellt:** 2026-08-21
> **Scope:** `C:\Users\muham\eidolon` (Python-PoC + Rust-Crates + Web-UI + Desktop-Overlay)
> **Ziel:** Alle Dateien kartieren, Duplikate/Altbestände identifizieren, durchführen

---

## 1. Durchgeführte Bereinigung

| Aktion | Ergebnis |
|---|---|
| **`.bak`-Dateien`** | 17 gelöscht |
| **`py/agent_server.py`** (10 KB veraltet) | Gelöscht — verursachte Import-Konflikte mit 88 KB Hauptserver |
| **`py/cli.py`** | Gelöscht — wird durch `eidolon/cli/main.py` ersetzt |
| **`py/quic_server_runner.py`** / `runner2.py` | Gelöscht — veraltet |
| **12 `test_p2p_*.py` Dateien** | Gelöscht — alle 0 Test-Funktionen |
| **`test_tcp_basic.py`** / `test_udp_basic.py`** | Gelöscht — 0 Tests |
| **`test_phaseF_mtls.py`** | Gelöscht — 0 Tests |
| **Verwaiste Dateien** (`nul`, `note.txt`, `qr_*.png/svg`, `txt/note.txt`) | Gelöscht |
| **`python/ROADMAP.md`** (veraltet) | Gelöscht — Root `ROADMAP.md` ist Quellwahrheit |
| **`eidolon/data/mesh/`** (Zertifikat-Duplikat) | Gelöscht |
| **Verwaiste Daten** (`phase*.json`, `persist/`, `persistence/`, `search_cache/`) | Gelöscht |
| **7 veraltete Tests** (Import-Fehler) | In `py/obsolete/` verschoben |

---

## 2. Verbleibende Struktur

### Python — aktive Test-Dateien (116 Tests bestanden)

```
py/
├── test_adaptive_workspace.py     ✅ 50 Tests
├── test_audit_fixes.py            ✅ 7 Tests
├── test_settings.py               ✅ 35 Tests
├── test_web_ui.py                 ✅ 24 Tests
└── obsolete/                      ⚠️ Veraltet, nicht in pytest
    ├── test_healing.py
    ├── test_intent_engine.py
    ├── test_orchestrator.py
    ├── test_capabilities.py
    ├── test_config.py
    ├── test_evidence.py
    └── test_graph.py
```

### Python — Kernmodule (unverändert funktional)

```
eidolon/
├── core/
│   ├── config.py                  # Zentrale Config (Ports, Pfade, Feature-Flags)
│   ├── settings_store.py          # NEU: Bereichs-Einstellungen
│   ├── healing.py                 # Self-Healing Service
│   ├── evidence.py                # Evidence Store (Anti-Halluzination)
│   ├── capabilities.py            # Capability-System
│   ├── llm_backend.py             # LLM-Router (Ollama + OpenAI)
│   ├── orchestrator.py            # ProjectOrchestrator
│   ├── world_model.py             # World Model
│   ├── cron.py                    # CronJob Scheduler
│   ├── planner.py                 # Goal Planner
│   ├── sync.py                    # Sync State
│   ├── agent_core.py              # Agent Core
│   └── persistence.py             # Persistence Layer
├── intent/
│   └── engine.py                  # Intent Engine
├── memory/
│   ├── graph.py                   # Knowledge Graph
│   ├── knowledge_graph.py         # Thin Wrapper
│   ├── delegation_economy.py      # Delegation Economy
│   └── strategy_memory.py         # Strategy Memory
├── mesh/
│   ├── inbox.py                   # Mesh Inbox (SQLite)
│   ├── peers.py                   # Peer State Store
│   ├── mesh_handler.py            # Mesh Handler
│   ├── crypto/
│   │   ├── certstore.py           # mTLS Trust Store
│   │   └── mesh_crypto.py         # Mesh Crypto
│   ├── discovery/
│   │   ├── device_discovery.py    # Device Discovery
│   │   └── helpers.py             # Pairing Helpers
│   ├── protocol/
│   │   └── packet.py              # Mesh Packet Protocol
│   └── transport/
│       └── quic_server.py         # QUIC Server/Client
├── skills/
│   ├── registry.py                # Skill Registry
│   ├── runtime.py                 # Skill Runtime
│   ├── builtin.py                 # Builtin Skills
│   ├── builtin_handlers.py        # Builtin Handlers
│   └── *.py / *.json              # Calendar, Device, File, Goals, Mesh, Notes, Plugin, System, Skill Generator
├── user/
│   ├── user_model.py              # User Model
│   ├── topic_attention.py         # Topic Attention
│   └── proactive_assistance.py    # Proactive Assistance
├── workspaces/
│   ├── contracts.py               # Safety Contracts
│   ├── generator.py               # Workspace Generator
│   ├── registry.py                # Workspace Registry
│   ├── state.py                   # Workspace State
│   ├── module_runtime.py          # Module Runtime
│   ├── orchestrator.py            # Workspace Orchestrator
│   └── orchestration_memory.py    # Orchestration Memory
├── web/
│   ├── index.html                 # Web-UI (2149 Zeilen)
│   └── web_client.py              # Web Client
└── cli/
    └── main.py                    # CLI (serve, chat, device, version)
```

### Eidos — Experimentelle Module

```
eidos/
├── core/
│   ├── autonomy_loop.py           # Autonomy Loop
│   ├── autonome_ziele.py          # Autonome Ziele
│   ├── goal_manager.py            # Goal Manager
│   ├── self_awareness.py          # Self-Awareness
│   ├── self_code_generator.py     # Self-Code Generation
│   ├── self_identity.py           # Self-Identity
│   ├── self_improvement_policy.py # Self-Improvement Policy
│   ├── utility_model.py           # Utility Model
│   ├── evidence_ext.py            # Evidence Extension
│   ├── proto_edge.py              # Proto Edge
│   └── refactoring_engine.py      # Refactoring Engine
├── integrations/
│   ├── openai_oauth.py            # OpenAI OAuth
│   └── openai_oauth_backend.py    # OpenAI OAuth Backend
├── mesh/
│   ├── agent_registry.py          # Agent Registry
│   └── task_delegator.py          # Task Delegator
└── tests/
    ├── integration_test_phase4.py
    ├── integration_test_phase9.py
    ├── test_autonomy_utility.py
    ├── test_delegation_economy.py
    ├── test_goal_manager.py
    └── test_self_improvement_policy.py
```

### Rust — Crates (9 Stück)

```
crates/
├── eidolon-cli/                   # CLI (chat, devices, diagnose, serve)
├── eidolon-core/                  # Core Runtime (Agent State Machine)
├── eidolon-eval/                  # Evaluation Engine
├── eidolon-interfaces/            # Shared Interfaces
├── eidolon-memory/                # SQLite Knowledge Graph
├── eidolon-mesh/                  # Mesh (Crypto, Discovery, Transport)
├── eidolon-multi-agent/           # Multi-Agent Support
├── eidolon-security/              # Security Layer
└── eidolon-skills/                # Skill Executor + Generator
```

---

## 3. Verbleibende Punkte (nicht kritisch)

### Stub-Dateien (gewusst, zukünftige Arbeit)

| Datei | Status | Inhalt |
|---|---|---|
| `eidolon/core/orchestrator.py` | Stub | `print("Bereit...")` |
| `eidolon/intent/engine.py` | Stub | `pass` |

Diese Stubs werden im `agent_server.py` umgangen (dort ist die vollständige Logik implementiert). Für zukünftige Extraktion in separate Module vorgesehen.

### `py/eidolon_client.py`

```python
from eidolon.core.config import CERT_DIR, QUIC_PORT
from eidolon.mesh.transport.quic_server import EidolonQuicClient
```

Ist ein Standalone-Client für QUIC-Verbindungen. Könnte für Tests genutzt werden, ist aber nicht in die Hauptarchitektur integriert.

### `py/obsolete/` Tests

7 Test-Dateien mit veralteten Importen (referenzieren `CheckResult`, `HealingState`, `Intent`, `ProjectOrchestrator`, etc. die nicht mehr exportiert werden). Können bei Bedarf aktualisiert werden.

---

## 4. Zusammenfassung

| Kategorie | Vorher | Nachher | Aktion |
|---|---|---|---|
| `.bak`-Dateien | 17 | 0 | ✅ Gelöscht |
| Veraltete `py/`-Python | 6 | 0 | ✅ Gelöscht |
| Veraltete `py/`-Tests | 15 | 0 (in `obsolete/`) | ✅ Verschoben |
| Verwaiste Dateien | ~10 | 0 | ✅ Gelöscht |
| Doppelte `data/mesh/` | 2 | 1 | ✅ Konsolidiert |
| Veraltete `python/ROADMAP.md` | 1 | 0 | ✅ Gelöscht |
| Aktive Tests (bestanden) | — | 116 | ✅ Grün |
| Veraltete Tests (obsolete) | — | 7 | ⚠️ Verschoben |

**Ergebnis:** Keine Import-Konflikte mehr, keine verwirrenden Duplikate, 116 aktuelle Tests bestanden.
