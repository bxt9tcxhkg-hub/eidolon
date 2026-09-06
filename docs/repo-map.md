# Repo Map — Active vs Generated vs Historical

> Zweck: schnelle Navigation ohne Wahrheitsdrift. Diese Datei sagt nicht, **was** Eidolon sein soll; sie sagt, **wofür welcher Pfad im Repo steht**.

## 1. Aktive Produktwahrheit
Diese Dokumente definieren Soll, Istbild und Prioritäten:

- `docs/eidolon-specification.md` — kanonisches Produktsoll
- `docs/repo-boundaries.md` — Grenz- und Interpretationsregeln
- `docs/eidolon-spec-to-system-mapping.md` — aktueller Soll/Ist-Abstand
- `README.md` — kompakter Einstieg
- `ARCHITECTURE.md` — aktuelles Implementierungsbild
- `ROADMAP.md` — offene Prioritäten
- `AGENT.md` — Entwicklungs- und Verifikationsprotokoll

## 2. Aktiver Code

### Python-Produktpfade
- `python/agent_server.py` — FastAPI-Entrypoint
- `python/eidolon/` — Produktlogik, Routen, Operate, Workspaces, Rollen, Core
- `python/eidolon/web/` — aktive Weboberfläche
- `python/eidolon/web/nav_contract.py` — Alltagsweg vs. Mehr-Labels (Nav-Vertrag)

### Rust-Pfade (quarantiniert, nicht live)
- `crates/` — CLI (Client gegen FastAPI), experimentelle Runtime, Mesh-/Memory-/Eval-/Skills-/Core-Bibliotheken
- `Cargo.toml`, `Cargo.lock` — Workspace-Root
- Rust ist **nicht** die live Produktserver-Runtime und darf die Python-Ports `8002` / `4434` / `8001` nicht belegen

### Verifikation
- `tests/` — aktive Python-Verifikation
- `pytest.ini` — erzwingt aktive Testgrenzen

## 3. Generierte Laufzeitdaten
Diese Pfade sind **nicht** Quellwahrheit. Sie entstehen durch Nutzung, Tests, Dogfooding oder Runtime-Start:

- `%LOCALAPPDATA%/Eidolon/state/` — kanonischer externer State-Root für Operate, Evidence, Mesh, User, Backups, Browser, Voice, Generated-Artefakte
- `%LOCALAPPDATA%/Eidolon/state/_legacy_repo_snapshot/` — archivierte frühere Repo-State-Bäume
- `dogfood-output/` — Dogfood-/Prüfartefakte

Regel: Diese Pfade dürfen Verhalten belegen, aber **nicht** Architektur- oder Produktwahrheit definieren.

## 4. Historische / sekundäre Artefakte
- `docs/archive/` — verschobene historische Root-Analysen und Alt-Audits
- `docs/findings/` — Audit-Findings; nur aktiv, wenn nicht superseded
- `%LOCALAPPDATA%/Eidolon/state/backups/` — Runtime-Archiv, keine aktive Produktquelle
- `sketches/` — explorative Konzepte, keine produktive Wahrheit
- `.hermes/plans/` — Planungs- und Denkspuren
- ältere Root-Dateien außerhalb der aktiven Wahrheit sind Referenz, nicht Kanon

## 5. Navigation in der Praxis
Wenn du dich orientieren willst:

1. **Produkt verstehen:** `docs/eidolon-specification.md`
2. **Aktuelle Lücken sehen:** `docs/eidolon-spec-to-system-mapping.md`
3. **Konkrete Implementierung finden:** `python/eidolon/` und `python/agent_server.py`
4. **UI prüfen:** `python/eidolon/web/`
5. **Verifikation prüfen:** `tests/` und `python -m pytest -q`
6. **Historie nur bei Bedarf:** `docs/archive/`, `docs/findings/`, `%LOCALAPPDATA%/Eidolon/state/backups/`

## 6. Anti-Drift-Regel
Wenn ein Fakt nur in einem Archiv-, Backup- oder Runtime-Pfad steht, ist er **nicht automatisch aktuell**. Produktaussagen müssen immer auf aktiven Docs + Live-Code + Tests beruhen.
