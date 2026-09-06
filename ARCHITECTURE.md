# ARCHITECTURE — Eidolon Central Agentic System

> Status: aktuelles Implementierungsbild des aktiven Produktkerns. Diese Datei beschreibt **Ist-Architektur**, nicht Wunschdenken.

## Architektur in einem Satz
Eidolon ist derzeit ein **Python-FastAPI-System** (einzige live Runtime) mit gemeinsamem Work-Context-Kern für Chat und Operate, Workspace-/Projektlogik, Rollenregister und modularisierter Web-Oberfläche; technische Nebenflächen wie Mesh, Healing und Code-Mutation existieren, sind aber produktlogisch nachgeordnet. Rust-Crates sind quarantiniert und teilen nicht die Live-Ports.

## Primäre Ebenen

### 1. Product / Conversation Layer
- `python/eidolon/chat_runtime.py`
- `python/eidolon/chat_route_support.py`
- Erzwingt knappen Mitspieler-Vertrag für Arbeit (3–5 kurze Zeilen, höchstens eine Aktion oder eine Frage, kein Intention/Richtungen/Empfehlung-Schema)
- `POST /chat` und `GET /chat/context` ziehen ihren Runtime-Kontext über denselben `session_payload`-Pfad
- Baut Runtime-Kontext aus Chat, Workspace und Operate-Snapshot auf Basis des `work_context_kernel`
- Fängt generische Assistentenantworten und Essay-Schema ab und fällt auf eine kurze, geerdete Board-Angebot-Antwort zurück

### 2. Operate Kernel
- `python/eidolon/operate/contracts.py`
- `python/eidolon/operate/service.py`
- `python/eidolon/operate/bridge.py`
- Modelliert Session, Objective, Run, Approval, Blocking Issue, Evidence, Transition, Next Action
- Dient als wahrheitsfähiger Arbeitskern für sichtbaren Fortschritt

### 3. Workspace / Project Layer
- `python/eidolon/workspaces/`
- Liefert Projekt-/Workspace-Zustand und Runtime-Payloads
- Workspace-Payload-, Context- und Assistance-Aufbereitung läuft über kleine Fassaden plus spezialisierte Hilfsmodule
- Bridge synchronisiert aktive Workspaces in den Operate-Kernel

### 4. Bot Role Layer
- `python/eidolon/bots/role_registry.py`
- Trennt aktive Rollen von definierten Vorlagen
- Erzwingt Freigabe für dauerhafte, freigabepflichtige Rollen

### 5. Application Layer
- `python/agent_server.py`
- Integrationspunkt für API, Produktlogik und UI-Auslieferung
- **Einzige live Runtime:** Python FastAPI auf `EIDOLON_HTTP_PORT` (Standard `8002`)
- Runtime-Service-Erzeugung läuft über kleine Contracts-/Bootstrap-/Auth-Module statt über eine dichte Einzeldatei
- Live geprüft: 162 Routes im aktuellen App-Objekt

### 5b. Rust-Quarantäne
- `crates/` bleiben im Repo (CLI gegen FastAPI, experimentelle Runtime, Bibliotheken)
- Nicht löschen, nicht als zweiten Produktserver starten
- `eidolon-runtime` darf `8002` / `4434` / `8001` nicht binden; Defaults sind `18002` / `14434` / `18001`
- `Runtime::new` bricht ab, wenn ein Python-Live-Port gesetzt wird

### 6. Web UI Layer
- `python/eidolon/web/index.html`
- `python/eidolon/web/app-shell.css`
- `python/eidolon/web/components/app-components.css`
- CSS ist nach Shell-, Chat- und Goals-Slices in Importdateien aufgeteilt
- Dark-Theme bleibt Standard, mit wärmeren Neutralen, Display-Typo und reicherem Akzent; Idle-Signature atmet
- Arbeitsspur (`data-work-trace`) zeigt Bereit / Wartet / Als Nächstes aus Kernel- und Sessiondaten, ohne Placebo-Aktivität
- Default-Einstieg ist Chat (`/#chat`); Alltagsweg ist Chat / Projekte / Arbeit. Operate bleibt `#operate` / Nav „Arbeit“. Systemflächen hängen hinter Mehr (Betrieb / Technik), nicht in der Primärnav
- Chat-Tür ist Titel + Composer, optional eine Projektzeile; Freigaben/Blocker/Next Action bleiben in Arbeit und erscheinen im Chat nur bei echter laufender Handlung
- Chat, Arbeit und Projektfläche lesen denselben `work_kernel`-/Operate-Snapshot; Projektmutationen geben denselben Snapshot zurück
- Projektbildung ist über `POST /workspaces/formation` explizit; `active_project` braucht sichtbare Bestätigung
- Chat-Kandidaten entstehen deterministisch aus Vorhaben-Nachrichten; Bestätigung füllt textgebundene Board-Karten (Bedingungen in Notizen, idempotentes Seed) und kann eine echte Operate-Freigabe öffnen
- Projektfläche zeigt im Idle **Neues Projekt** plus leeres Planungsboard; der Operate-Überblick (Zustand/Ziel/Blocker/Freigaben) bleibt im Idle verborgen
- Offenes Projekt: Board zuerst (Spaltenname + Zahl); Titel/Status/Chat/Arbeit hinter einer Projekt-Disclosure; Chat/Arbeit nur als kleine Nebenwege
- Projekt- und Elementmutationen (Rename, Status, Gruppe, Reihenfolge, Archiv, Streichen) schreiben gegen bestehende Projekt-APIs
- Keine fest verdrahteten Domänen-Pakete (kein Training-/Instagram-/Reise-UI)
- Arbeit im Idle: eine Karte mit Chat-Start, optional Übernahme aus der Projektfläche, kurzer Hinweis auf Freigaben
- Arbeit mit Lauf: Ziel, nächster Schritt, Freigaben/Blocker nur wenn vorhanden; Rest in zugeklappten Details
- Motion bestätigt nur echte Mutationen (Verschieben, Status, Freigabe, neues Projekt) und achtet `prefers-reduced-motion` sowie Settings `ui.animations`

### 7. LLM-Provider-Registry
- `python/eidolon/core/llm_provider_catalog.py` beschreibt Ollama, den OpenAI-kompatiblen HTTP-Stecker und Codex-OAuth
- Chat/`complete()` geht über `llm_fallback.py`: gewählter Anbieter zuerst, danach die eindeutige `fallback_chain`
- Die Ersatzkette ist in den Settings sortierbar und liegt in Settings/Registry; leer oder ungültig wird ehrlich abgelehnt, nicht still korrigiert
- Chat (Execute-Tür) und Operate setzen Settings nur auf ausdrücklichen Wunsch: `POST /settings/apply` und `POST /api/v1/operate/settings/apply`; Secrets bleiben draußen
- `/llm/connection`, Chat-Kontext und „Welche Fehler…“ zeigen erkannte LLM-/Healing-/Health-Probleme ohne Schlüsselwerte
- OpenAI-kompatibel ist `base_url` + API-Schlüssel + Modell; Presets (Groq, OpenRouter, …) setzen nur Defaults
- OAuth wird nur für `openai_oauth` angeboten; `/llm/connection` und Settings zeigen Status ohne Schlüsselwerte

## Aktuelle Hauptschulden
- `python/agent_server.py` ist weiter ein großer Integrationspunkt
- `python/eidolon/web/index.html` bleibt groß und mischt Produktsemantik mit UI-Implementierung
- `python/eidolon/web/app-shell.js` bleibt ein großer SPA-Hotspot
- mehrere historische Dokumente im Repo können ohne Boundary-Regeln fehlgelesen werden, obwohl Archiv-/Finding-Readmes das jetzt explizit begrenzen

## Aktuelle Wahrheitsregel
- Produkt-Soll: `docs/eidolon-specification.md` (Parität/Differenz/Ehrlichkeit: `docs/eidolon-evolution-stage.md`)
- Implementierungs-Ist: Live-Code + Tests + Endpoint-Antworten
- Aktive Fortschrittsquelle: `ROADMAP.md`
- Findings und Root-History sind Referenz, nicht Primärwahrheit
- Dieses Dokument dient der Einordnung der aktiven Struktur, nicht der Übersteuerung der Spezifikation
