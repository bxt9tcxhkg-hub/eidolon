# EIDO-006 — Dashboard zeigte teils Lade-/Minus-Platzhalter trotz echter Daten

- **ID:** `EIDO-006`
- **Titel:** Dashboard nutzte falsche Response-Shapes und ließ Statuskarten künstlich leer
- **Primärkategorie:** `placeholder`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `ui`
- **Surface:** `web`
- **Gefunden in Block:** `D`

---

## Claim
> Das Status-Dashboard zeige die realen Runtime-/Storage-/Komponentendaten.

## Reality
Vor dem Fix:
- `Komponenten` blieb auf `Lade…`
- `loadSystemMetrics()` erwartete Felder wie `memory_mb` direkt auf Root-Ebene, obwohl `/system/metrics` `process` und `system` liefert
- `loadSystemStorage()` erwartete `project_mb`/`backups_mb`, obwohl `/system/storage` `areas` liefert

Dadurch wirkte das Dashboard teils unvollständig, obwohl echte Daten vorhanden waren.

---

## Fix
- `python/eidolon/web/index.html`
  - `loadHealth()` rendert jetzt `dash-components` real aus `/health.components`
  - `loadSystemMetrics()` nutzt `process` und `system`
  - `loadSystemStorage()` nutzt `areas`
- Vertragstest ergänzt

## Verifikation
```text
pytest: 14 passed, 1 warning
node --check: inline scripts ok, workspace-ui.js ok
```

Live visuell geprüft:
- `Komponenten` zeigt jetzt u. a.
  - Knowledge Graph
  - QUIC-Transport → `not_wired`
  - Self-Healing → `not_wired`
  - Evidence Store
  - Ausführungsziele
  - Sicherungen
- keine künstliche `Lade…`-Daueranzeige mehr bei vorhandenen Daten

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
