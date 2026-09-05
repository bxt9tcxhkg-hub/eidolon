# AGENT.md — Eidolon Development Protocol

> **Zweck dieser Datei:** Entwicklungs- und Verifikationsregeln für Änderungen an Eidolon.
> **Sie ist nicht die Produktspezifikation.** Die kanonische Produktwahrheit liegt unter `docs/eidolon-specification.md` und den dort referenzierten Vertragsdokumenten.

## Dokumenthierarchie
1. **Produkt-Soll:** `docs/eidolon-specification.md` + verlinkte Vertragsdokumente
2. **Repo-Grenzen und Interpretationsregeln:** `docs/repo-boundaries.md`
3. **Repo-Navigation / aktive Pfadklassen:** `docs/repo-map.md`
4. **Architektur-Istbild:** `ARCHITECTURE.md`
5. **Fortschrittsstand / offene Prioritäten:** `ROADMAP.md`
6. **Diese Datei:** Wie Änderungen evidenzbasiert entwickelt und verifiziert werden

Wenn diese Ebenen widersprüchlich wirken:
- Produkt-Soll gewinnt gegen ältere Pläne
- Live-Code/Runtime gewinnt gegen veraltete Implementierungsbehauptungen
- Mapping-, Audit- und Roadmap-Dokumente müssen dann aktualisiert werden

## Kernregeln
- Keine Placebos, keine Fake-Erfolge, keine erfundenen Fähigkeiten
- Sichtbare UI-Elemente müssen echte Endpunkte/Mutationen nutzen oder ehrlich deaktiviert sein
- Chat, Operate, Projekte, Rollen und Freigaben müssen dieselbe Arbeitswahrheit sprechen
- Dauerhafte Produktentscheidungen gehören in die Spec-Dokumente, nicht nur in Runtime-Code

## Pflichtprüfung vor Aussagen und Merges
1. Relevante Specs lesen
2. Betroffene Runtime-/UI-Pfade prüfen
3. Reale Verifikation ausführen (`pytest`, Endpoint-Checks, UI-Contract-Checks)
4. Drift in README / ARCHITECTURE / ROADMAP / Mapping mitziehen

## Aktive Implementierungsflächen
- `python/agent_server.py`
- `python/eidolon/chat_runtime.py`
- `python/eidolon/operate/`
- `python/eidolon/workspaces/`
- `python/eidolon/bots/`
- `python/eidolon/core/`
- `python/eidolon/web/`
- `tests/`

## Historische / sekundäre Artefakte
- `.hermes/plans/` → Planungs- und Denkspuren, nicht aktive Produktwahrheit
- `docs/findings/` → Audit-/Finding-Historie; kann superseded sein
- `%LOCALAPPDATA%/Eidolon/state/backups/` → Runtime-Archiv, keine aktive Produktquelle
- ältere Analyse-/Phase-Dokumente im Root → Referenz, nicht kanonische Sollquelle

## Runtime-State-Regel
- Aktiver Runtime-State liegt außerhalb des Repos unter `%LOCALAPPDATA%/Eidolon/state/`
- Repo-interne `data/`- oder `python/data/`-Pfadnutzung gilt als Drift und muss auf `eidolon.core.config`-State-Resolver zurückgeführt werden
- Frühere Repo-State-Bäume liegen nur noch als Archiv unter `%LOCALAPPDATA%/Eidolon/state/_legacy_repo_snapshot/`

## Arbeitsgrenze trotz globalem Git-Root
`git rev-parse --show-toplevel` zeigt aktuell nicht isoliert auf das Eidolon-Projekt, sondern auf `C:/Users/muham`.

Deshalb gilt:
- Pfadbasierte Repo-Grenzen aus `docs/repo-boundaries.md` sind verbindlich
- globale `git status`-Aussagen sind ohne Pfadkontext nicht ausreichend
- Verifikation muss immer über konkrete Dateien, Tests und Endpunkte erfolgen

## Verifikation
Standardpfad:
```bash
python -m pytest -q
```

Gezielte Verträge zusätzlich bei betroffenen Bereichen:
- Chat: `tests/test_chat_runtime.py`
- UI/API-Wahrheit: `tests/test_web_ui_contracts.py`
- Idle-/Wärme-Verträge: `tests/test_empty_state_ui_contracts.py`, `tests/test_warmth_work_trace_ui_contracts.py`
- Formation-Loop: `tests/test_formation_loop_contracts.py`
- Operate-Contracts: `tests/test_operate_api_contracts.py`, `tests/test_operate_ui_contracts.py`

## Änderungsregel
Wenn du Produktlogik änderst, aktualisiere in derselben Änderung auch:
- die betroffene Spec oder das Mapping, wenn sich der Soll/Ist-Abstand geändert hat
- die Tests, die die neue Wahrheit absichern
