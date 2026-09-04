# EIDOLON — Zentrales agentisches Hauptsystem

> **Kanonische Produktsollquelle:** `docs/eidolon-specification.md`
> 
> Diese README beschreibt den aktuellen, verifizierten Produktkern in kompakter Form. Historische Planungs- und Mesh-Schwerpunkte bleiben im Repo als Referenz, sind aber nicht mehr die primäre Produktdefinition.

## Produkt in einem Satz
Eidolon ist ein **arbeitsführendes agentisches Hauptsystem**, das Gespräch, Projektbildung, Operate-Zustand, Rollenorganisation und adaptive Arbeitsflächen unter einer konsistenten Arbeitslogik zusammenführt.

## Primäre Produktlogik
- **Chat ist der Einstieg** (`/#chat`)
- **Operate ist der sichtbare Arbeitskern** hinter dem Chat, nicht die Starttür
- **Projekte/Workspaces** sind die strukturierte Arbeitsfläche (Planung: Zusammengehörig / Geplant / In Arbeit / Fertig)
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
- Web-UI startet in Chat; Projektfläche und Arbeit (Operate) sind erreichbar, ohne die Starttür zu sein
- Projektplanung zeigt modellierte Status-Eimer und erlaubt Umbenennen/Status/Reihenfolge, soweit die APIs existieren
- `/identity` liefert Produktrolle und aktive/definierte Rollen getrennt
- Runtime-State liegt außerhalb des Repos unter `%LOCALAPPDATA%/Eidolon/state/`
- `python -m pytest -q` besteht

## Aktive Wahrheitsquellen
- Produkt-Soll: `docs/eidolon-specification.md`
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
