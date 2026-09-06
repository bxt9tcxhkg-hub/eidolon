# EIDOLON — Zentrales agentisches Hauptsystem

> **Kanonische Produktsollquelle:** `docs/eidolon-specification.md`
> 
> Diese README beschreibt den aktuellen, verifizierten Produktkern in kompakter Form. Historische Planungs- und Mesh-Schwerpunkte bleiben im Repo als Referenz, sind aber nicht mehr die primäre Produktdefinition.

## Produkt in einem Satz
Eidolon ist ein **arbeitsführendes agentisches Hauptsystem**, das Gespräch, Projektbildung, Operate-Zustand, Rollenorganisation und adaptive Arbeitsflächen unter einer konsistenten Arbeitslogik zusammenführt.

## Primäre Produktlogik
- **Chat ist der Einstieg** (`/#chat`)
- **Operate ist der sichtbare Arbeitskern** hinter dem Chat, nicht die Starttür
- **Projekte/Workspaces** sind die strukturierte Arbeitsfläche (Planung: Zusammengehörig / Geplant / In Arbeit / Fertig / Archiv)
- **Karten/Widgets** sind nur ein generisches Gerüst (Slots + Typen). Keine fest verdrahteten Domänen-Pakete
- **Bots** sind organisatorische Rollen, keine Personas
- **Autonomie** ist erlaubt, aber sichtbar und begrenzt

## Live-Runtime
**Python FastAPI ist der einzige live Produktserver.** Start: `python python/agent_server.py` (Standardport `8002`).

Rust-Crates bleiben im Repo (CLI, experimentelle Runtime, Mesh-Bibliotheken), sind aber **quarantiniert**:
- Sie dürfen die Live-Ports `8002` / `4434` / `8001` nicht belegen
- `eidolon-runtime` bindet standardmäßig `18002` / `14434` / `18001` und bricht ab, wenn ein Python-Live-Port gesetzt wird
- Die Rust-CLI darf den Python-Server auf `8002` als Client ansprechen
- Crates wurden nicht gelöscht

## Verifizierter Ist-Stand
- FastAPI-Produktserver vorhanden — einzige live Runtime
- Chat-Session-System mit Runtime-Context vorhanden
- Operate-Kernel mit Run-/Objective-/Approval-/Blocker-/Evidence-Modell vorhanden
- Workspace-Bridge in Operate vorhanden
- Web-UI startet in Chat; Alltagsweg ist Chat / Projekte / Arbeit. Technikflächen (Health, Healing, Katalog, Mesh, Ausführung, Helfer-Protokoll, KI-Diagnosen) liegen hinter Mehr / Einstellungen
- Idle-Chat ist eine Tür (Titel + Composer, optional eine Projektzeile); Dark-Theme ist wärmer, Arbeitsspur zeigt Bereit/Wartet/Nächstes in Arbeit/Projektfläche aus echten Kernel- und Sessiondaten
- Freigaben, Blocker und nächster Schritt bleiben in Arbeit und lösen dieselben Operate-APIs aus; Chat listet sie nicht als Landing-Dashboard
- Projektplanung erlaubt Rename, Status, Gruppe, Reihenfolge, Ablegen und Streichen gegen persistierte Projekt-APIs
- Chat, Arbeit und Projektfläche lesen Freigaben/Blocker/Next aus demselben `work_kernel`/`operate`-Snapshot; Projektmutationen geben denselben Snapshot zurück statt eines leeren Parallelpfads
- Projektbildung `chat_topic` → `project_candidate` → `active_project` ist ein expliziter Vertrag mit sichtbarer Bestätigung vor dauerhaftem Projekt; stille Projekt-Bots gibt es nicht. Kandidaten entstehen auch ohne LLM; Bestätigung füllt unterscheidbare Board-Karten aus dem Vorhaben-Text (Bedingungen in Notizen, idempotentes Seed)
- Generische Slots (Kontext, Ziel, Zustand, Next, Freigabe, Blocker, Inbox, Evidenz) werden aus Kernel/Workspace gespeist, nicht aus Domänen-Paketen
- `/identity` liefert Produktrolle und aktive/definierte Rollen getrennt
- Runtime-State liegt außerhalb des Repos unter `%LOCALAPPDATA%/Eidolon/state/`
- `python -m pytest -q` besteht für die neuen Formation-/Work-Truth-/Planning-Verträge; in dieser Umgebung zusätzlich 4 vorbestehende Env-Fehler (kein Live-Ollama, kein `aioquic`, keine Codex-CLI)

## Aktive Wahrheitsquellen
- Produkt-Soll: `docs/eidolon-specification.md` (inkl. `docs/eidolon-evolution-stage.md`)
- Soll/Ist-Mapping: `docs/eidolon-spec-to-system-mapping.md`
- Repo-Grenzen: `docs/repo-boundaries.md`
- Repo-Navigation: `docs/repo-map.md`
- Implementierungsbild: `ARCHITECTURE.md`
- Fortschritt/Prioritäten: `ROADMAP.md`

## Start / Verifikation
```bash
python python/agent_server.py
# Browser: http://127.0.0.1:8002/#chat
# Projektplanung: Projektfläche öffnen, Projekt wählen — Standardansicht ist Planung
python -m pytest -q
python scripts/repo_hygiene_check.py
```
