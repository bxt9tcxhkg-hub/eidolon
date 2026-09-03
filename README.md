# EIDOLON — Zentrales agentisches Hauptsystem

> **Kanonische Produktsollquelle:** `docs/eidolon-specification.md`
> 
> Diese README beschreibt den aktuellen, verifizierten Produktkern in kompakter Form. Historische Planungs- und Mesh-Schwerpunkte bleiben im Repo als Referenz, sind aber nicht mehr die primäre Produktdefinition.

## Produkt in einem Satz
Eidolon ist ein **arbeitsführendes agentisches Hauptsystem**, das Gespräch, Projektbildung, Operate-Zustand, Rollenorganisation und adaptive Arbeitsflächen unter einer konsistenten Arbeitslogik zusammenführt.

## Primäre Produktlogik
- **Chat ist der Einstieg**
- **Operate ist der sichtbare Arbeitskern** für Zustand, Freigaben, Blocker, Subagenten, Evidenz und nächsten Schritt
- **Projekte/Workspaces** sind die strukturierte Arbeitsfläche
- **Bots** sind organisatorische Rollen, keine Personas
- **Autonomie** ist erlaubt, aber sichtbar und begrenzt

## Verifizierter Ist-Stand
- FastAPI-Produktserver vorhanden
- Chat-Session-System mit Runtime-Context vorhanden
- Operate-Kernel mit Run-/Objective-/Approval-/Blocker-/Evidence-Modell vorhanden
- Workspace-Bridge in Operate vorhanden
- Web-UI mit Tabs für Chat, Leitstand, Projekte, Ziele, System, Mesh, Sicherungen, Stabilität, Fähigkeiten, Einstellungen, Code, Identität vorhanden
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
python -m pytest -q
python scripts/repo_hygiene_check.py
```
