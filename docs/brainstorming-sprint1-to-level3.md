# Brainstorming: Eidolon — Von Sprint-1 zur Evolutionstufe 3

## I. Ist-Stand (Sprint-1-Niveau)
- Rust-Core kompiliert (9/9 Crates), aber nur als Library
- Python-PoC live (Port 8000) mit 8 einfachen Skills
- UDP-Broadcast erkennt Test-Peer (`peer-001`), aber keine echte P2P-Verbindung
- QUIC-Server läuft (Port 4433/4455), aber nur Server-seitig
- SurrealDB-Placeholder, kein Knowledge-Graph in Produktion
- Kein Multi-Agent-Ökonomie-System (nur Rust-Strukturen)
- Desktop-Overlay (PyQt6) minim

## II. Vision (Evolutionstufe 3)
- Selbst-improvierender Agent mit LLM-gestützter Skill-Generierung
- Echte P2P-Geräte-Gerät-Kommunikation über QUIC/mDNS/BLE
- Multi-Agent-Ökonomie mit Reputation und Verhandlung
- Zero-Trust-Sicherheit mit Capability-Tokens
- SurrealDB-Knowledge-Graph mit semantischer Suche
- Desktop-Overlay mit Screenshot-Analyse (PyQt6)

---

## III. Brainstorming: Pfade zur Evolutionstufe 3

### A. Rust-Build-Problem lösen (kritisch!)

**Problem:** MSVC-Linker fehlt, `dlltool` nicht gefunden, MSYS2-hang

**Lösungsansätze:**
1. **Rust für `x86_64-pc-windows-msvc` kompilieren** (nicht GNU)
   - VS Code Build Tools via `winget install Microsoft.VisualStudio.2022.BuildTools`
   - MSVC-Workload: `Microsoft.VisualStudio.Workload.VCTools`
   - Dann: `cargo build --release` (Native Windows-Binary)

2. **Cross-Compilation auf Linux**
   - Build auf einem Linux-Rechner (`x86_64-pc-windows-gnu` oder `msvc`)
   - Binary zurück auf Windows kopieren

3. **Docker-basiertes Cross-Compile**
   - `docker run --rm -v ${PWD}:/src -w /src rust:latest bash -c "apt-get update && apt-get install -y mingw-w64 && cargo build --release --target x86_64-pc-windows-gnu"`

4. **Fallback: Rust als Library nur**
   - Rust bleibt als Bibliothek, Python als Hauptlogik
   - Rust-Parts (Memory, Skills, Eval) über `pyo3`-Bindings in Python integrieren

### B. Echte P2P-QUIC-Verbindung herstellen

**Problem:** Nur Server laufend, kein echter Client-Handshake

**Lösungsansatz:**
1. **Zwei Python-Prozesse starten** (Host + Client)
   - Host: `agent_server.py` (Port 8000 + QUIC 4455)
   - Client: `eidolon_client.py` (Neuer Prozess, verbindet sich via QUIC)
2. **QUIC-Client mit aioquic implementieren**
   - `EidolonQuicClient`-Klasse in `quic_server.py`
   - mTLS-Verifikation mit `server.crt` aus Host
3. **Mesh-Nachricht über QUIC senden**
   - Nachricht über QUIC-Stream an Client senden
   - Client speichert in `mesh_inbox.json`

### C. SurrealDB-Knowledge-Graph aktivieren

**Problem:** SurrealDB ist zu schwer für Windows-Build

**Lösungsansatz:**
1. **SQLite-basierter Graph** statt SurrealDB
   - Tabellen: `entities`, `relationships`, `episodes`
   - SQLite unterstützt JSON-Felder + rekursive Queries
2. **Python-Memory-Layer** (`eidolon.core.memory.graph`)
   - `get_or_create_entity()`, `relate()`, `search()`
3. **Rust-Memory-Crate als Interface**
   - `eidolon-memory` rust crate definiert Traits
   - Python-Implementierung erfüllt diese Traits

### D. Multi-Agent-Ökonomie aktivieren

**Problem:** Nur Rust-Strukturen, keine aktive Ökonomie

**Lösungsansatz:**
1. **In-Memory Wallet-System**
   - Jeder Agent (Host, peer-001) hat ein Wallet
   - Credits für Task-Delegation
2. **Reputations-Barometer**
   - UI-Anzeige der Reputation
   - Reputation aktualisiert bei erfolgreichen Tasks
3. **A2A-Protokoll über Mesh**
   - Nachrichtenformat: `"{\"type\":\"a2a_request\",\"task\":\"...\",\"to\":\"peer-002\",\"reward\":10}"`

### E. Self-Healing aktivieren

**Problem:** Placeholder-Struktur, keine echte Selbstreparatur

**Lösungsansatz:**
1. **Health-Check-Loop**
   - Periodisches Ping-Protokoll für alle Endpoints
   - Wenn `/mesh/quic-status` = false → Restart QUIC-Server
2. **Self-Healing-Skill**
   - Python-Skill: `restart-server`
   - Führt `agent_server.py` Neustart aus

### F. Desktop-Overlay erweitern

**Problem:** Grundgerüst, keine Screenshot-Analyse

**Lösungsansatz:**
1. **PyQt6-Overlay mit Nuitka-Compilierung**
   - `pyinstaller --onefile overlay.py` → exe
2. **Screenshot-Integration**
   - `pyautogui` oder `mss` für Bildschirmaufnahme
   - Bild an lokale Ollama-Instanz zur Analyse senden

### G. CLI erweitern

**Problem:** Nur `clidefault` (2 Befehle)

**Lösungsansatz:**
1. **Hermes-Agent-Skill-Autor** (`skill_manage` Tool) integrieren
2. **Erweiterte CLI-Befehle:**
   - `eidolon mesh-send` → Nachricht über P2P senden
   - `eidolon pairing-generate` → Pairing-Code erstellen
   - `eidolon skill-create` → Skill aus aktuellem Kontext erstellen
   - `eidolon self-heal` → Selbstreparatur starten

---

## IV. Prioritisierte Umsetzungs-Reihenfolge

| Rang | Feature | Aufwand | Ressourcen | Impact |
|---|---|---|---|---|
| **1** | **Rust-Build-Rustung (MSVC via VS Build Tools)** | Mittel | `winget install Microsoft.VisualStudio.2022.BuildTools` | Kritisch |
| **2** | **Echte P2P-QUIC-Verbindung (Host+Client)** | Mittel | 2 Python-Prozesse, mTLS-Certs | Hoch |
| **3** | **SQLite-Knowledge-Graph in Python** | Hoch | `sqlite3`, JSON-Datentypen | Hoch |
| **4** | **Multi-Agent-Ökonomie (Wallet + Reputation)** | Mittel | In-Memory, UI-Balken | Mittel |
| **5** | **Self-Healing Loop** | Niedrig | Health-Checks, Restart-Script | Mittel |
| **6** | **CLI erweitern (mesh-send, pairing, skill-create)** | Niedrig | Hermes-Agent-CLI-Build | Mittel |
| **7** | **Desktop-Overlay verfeinern (Screenshot-Analyse)** | Hoch | Nuitka, mss oder pyautogui | Niedrig |
| **8** | **SurrealDB ersetzen durch SQLite** | Hoch | Migration-Layer | Mittel |

---

## V. Setup-Analyse: Was reicht unser Setup?

| Anforderung | Status | Lösung |
|---|---|---|
| **MSVC-Build** | ❌ Fehlt | `winget install Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools"` |
| **Zwei Geräte** | ✅ Simuliert | Zweiten Python-Prozess auf localhost:8001 starten |
| **QUIC-Client** | ❌ Fehlt | `EidolonQuicClient` in `quic_server.py` implementieren |
| **mTLS-Peer-Zertifikat** | ❌ Teilweise | `certstore.py` erweitern um Peer-Certs |
| **SQLite-Knowledge-Graph** | ✅ Verfügbar | `sqlite3` ist in Python 3.11 enthalten |
| **Memory-Management** | ✅ Verfügbar | `data/persistence/` Struktur existiert |
| **Overlay-Compilierung** | ❌ Fehlt | `pyinstaller --onefile` für PyQt6-Overlay |

---

## VI. Nächste konkrete Schritte (nächste 2 Stunden)

1. **MSVC-Build-Tools installieren**
   ```bash
   winget install Microsoft.VisualStudio.2022.BuildTools --override "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --passive --norestart"
   ```

2. **Zweiten Python-Prozess starten** (Client-Peer)
   ```bash
   cd python
   python agent_server.py --peer-id peer-002 --port 8001 &
   python agent_server.py --peer-id peer-001 --port 8002 &
   ```

3. **QUIC-Client-Handshake implementieren**
   ```python
   # In quic_server.py
   class EidolonQuicClient:
       async def connect(self, host, port): ...
   ```

4. **Mesh-Nachricht über QUIC testen**
   ```bash
   curl -X POST http://localhost:8000/mesh/send \
     -d '{"to": "peer-002", "message": "Hallo von peer-001"}'
   ```
