# Repo Boundaries

> Status: kanonische Grenz- und Interpretationsregeln für dieses Repository.

## Aktive Produktwahrheit
Diese Dateien definieren das **Soll** von Eidolon:
- `docs/eidolon-specification.md`
- `docs/eidolon-product-identity.md`
- `docs/eidolon-core-workflow.md`
- `docs/project-formation-rules.md`
- `docs/eidolon-autonomy-contract.md`
- `docs/bot-organization-model.md`
- `docs/bot-role-requirements.md`
- `docs/eidolon-ui-workspace-architecture.md`

## Aktive Interpretations- und Entwicklungswahrheit
- `docs/eidolon-spec-to-system-mapping.md` → dokumentierter Soll/Ist-Abstand
- `docs/repo-map.md` → aktive Pfadnavigation und Trennung von Code vs Runtime vs Historie
- `ROADMAP.md` → aktueller Fortschritts- und Prioritätenstand
- `ARCHITECTURE.md` → aktuelles Implementierungsbild
- `AGENT.md` → Entwicklungs- und Verifikationsprotokoll

## Aktive Implementierungsflächen
- `python/`
- `python/eidolon/`
- `tests/`
- `docs/` (nur aktuelle Spec-/Mapping-/Boundary-Dokumente)
- `pytest.ini` (erzwingt die aktive Testgrenze)

## Externer Runtime-State
- Kanonischer Runtime-State liegt unter `%LOCALAPPDATA%/Eidolon/state/`
- Repo-interne `data/`- und `python/data/`-Bäume sind **nicht mehr** aktive Laufzeitwahrheit
- Frühere Repo-State-Inhalte wurden nach `%LOCALAPPDATA%/Eidolon/state/_legacy_repo_snapshot/` archiviert

## Historische / nicht-kanonische Artefakte
- `%LOCALAPPDATA%/Eidolon/state/backups/`
- `sketches/`
- `.hermes/plans/`
- ältere Root-Analysen und Phase-Dokumente
- `docs/findings/` sofern ein Finding explizit als `superseded` markiert ist

## Git-Arbeitsgrenze
Aktuell liegt der erkannte Git-Top-Level oberhalb des Projekts (`C:/Users/muham`).

Das bedeutet:
- `git status` enthält Rauschen außerhalb von Eidolon
- Diff-/Änderungsaussagen dürfen nicht blind als reine Projektwahrheit interpretiert werden
- repo-lokale Verifikation muss auf Pfade, Tests und aktive Implementierungsflächen gestützt werden, nicht nur auf den globalen Git-Status

Bis eine saubere Projektwurzel etabliert ist, gilt diese Datei als verbindliche Arbeitsgrenze.

## Testgrenze
`pytest` darf keine Archiv-, Backup- oder generierten Bäume als aktive Wahrheit behandeln.

Diese Regel wird aktuell technisch durch `pytest.ini` erzwungen (`data/backups`, `vendor`, `target`, `sketches`). Alte Repo-State-Bäume sollen nicht zurückkehren.

## Interpretationsregel
Wenn zwei Artefakte kollidieren:
1. Produkt-Spec gewinnt gegen historische Planung
2. Live-Code/Runtime gewinnt gegen veraltete Statusbehauptungen
3. Mapping/Roadmap/Architecture müssen nachgezogen werden
4. `AGENT.md` steuert den Entwicklungsprozess, ersetzt aber **nicht** die Produktspezifikation
