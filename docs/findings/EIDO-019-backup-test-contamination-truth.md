# EIDO-019 — Backup-Oberfläche zeigte Test-/Restore-Artefakte als echte verfügbare Sicherungen

- **ID:** `EIDO-019`
- **Titel:** Alte `test`, `test_manual` und `pre_restore` Backups kontaminierten die Live-Backup-Liste
- **Primärkategorie:** `placebo`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `backups`, `persistence`, `ui-truth`
- **Surface:** `web`, `api`, `persistence`
- **Gefunden in Block:** `next9`

---

## Claim
> Die Backup-Fläche zeigt reale verfügbare Sicherungen des Produkts.

## Reality
Die Live-UI zeigte vier alte Test-/Restore-Artefakte als verfügbare Backups:

- `*_test`
- `*_test_manual`
- `*_pre_restore` aus einem Test-Restore

Dadurch wirkten Test- und Verifikationsstände wie echte aktuelle Rollback-Punkte. Das ist besonders kritisch, weil `Wiederherstellen` ein destruktiver Produktflow ist.

---

## Fix
- Test-/Restore-Kontamination wurde archiviert:
  - `data/backups/test_backup_contamination_20260826T073350Z/`
- Der Live-Katalog wurde bereinigt:
  - vorher: 4 katalogisierte Backups
  - nachher: 0 echte sichtbare Backups
- Runtime-Backup-Service filtert künftig nicht-live Backups aus der sichtbaren Liste:
  - `test`
  - `dogfood`
  - `verification`
  - `fixture`
  - `metadata.live_visible == false`
  - `metadata.archived_contamination`
- Backup-Statistiken zählen nur noch sichtbare Live-Backups; `hidden_count` bleibt als Diagnosefeld erhalten.
- Die getrennte Core-Backup-Service-Implementierung wurde ebenfalls mit derselben Live-Filter-Logik gehärtet, damit spätere Konsolidierung keinen Rückfall erzeugt.

---

## Verifikation
```text
pytest: 31 passed, 1 warning
node --check: erfolgreich
```

Live/API nach Server-Neustart:
```json
{"ok": true, "count": 0, "hidden_count": 0, "backups": []}
```

Live/UI:
- Backup-Fläche zeigt:
  - `Backups 0 / 10`
  - `Speicher 0 MB`
  - `Keine Backups`
- sichtbar bleibt nur der echte Aktionsbutton:
  - `+ Neues Backup`
- keine Test-/Restore-Artefakte mehr als wiederherstellbare Sicherungen sichtbar

---

## Evidence
- `dogfood-output/backup-truth/02-backups-empty-after-runtime-filter.png`

---

## Abschluss
- **Verifiziert am:** 2026-08-26
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** Backup-Service-Duplikat in `agent_server.py` und `eidolon.core.backup_service` später konsolidieren, damit Logik nicht doppelt gepflegt werden muss.
