# EIDO-016 — Code- und Backup-Buttons waren nur teilweise echte UI-Flows

- **ID:** `EIDO-016`
- **Titel:** Code-Pflege nutzte Browser-Prompts; Backup-Aktionen hatten keine direkte, überprüfbare UI-Bindung
- **Primärkategorie:** `placebo`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `web-ui`, `buttons`, `code-maintenance`, `backups`
- **Surface:** `web`, `api`
- **Gefunden in Block:** `next6`

---

## Claim
> Web-UI-Buttons sind korrekt angebunden und funktionsfähig.

## Reality
Mehrere sichtbare Systempflege-/Backup-Aktionen waren nicht ausreichend echte Produktflows:

1. **Code-Analyse / Code-Reparatur**
   - `Analysieren` und `Reparieren` fragten Dateipfade per `prompt()` ab.
   - `Reparieren` sendete keine Issue-Beschreibung, obwohl `/code/fix` diese verlangt.
   - Fehlerantworten mit `{ok:false}` wurden nicht konsequent als Produktzustand gerendert.

2. **Backups**
   - `restoreBackup()` und `deleteBackup()` existierten nur als `prompt()`/`confirm()`-Flows.
   - Die Backup-Liste zeigte keine echten zeilenbezogenen Aktionen.
   - Dadurch waren Wiederherstellen/Löschen keine sauber sichtbaren, überprüfbaren UI-Flows.

---

## Fix
- `python/eidolon/web/index.html`
  - Code-Pflege hat jetzt echte Inline-Eingaben:
    - `#code-file-path`
    - `#code-issue`
  - `Analysieren` rendert die echte API-Antwort sichtbar im Codeblock.
  - `Reparieren` blockiert ohne Issue-Beschreibung ehrlich und rendert bei gültiger Eingabe den echten `proposal_only`-Response.
  - `prompt()` und `confirm()` wurden aus der Web-UI entfernt.
  - Backup-Liste rendert jetzt pro Backup echte Buttons:
    - `Wiederherstellen`
    - `Löschen`
  - Gefährliche Aktionen sind als Zwei-Klick-Arming umgesetzt:
    - `Restore bestätigen`
    - `Löschen bestätigen`
  - API-`{ok:false}` wird auch hier als Fehler behandelt.
- `python/agent_server.py`
  - `/code/fix` löst relative `file_path`-Angaben konsistent zur Analyse auf, statt `python/python/...`-Pfade zu erzeugen.

---

## Verifikation
```text
pytest: 27 passed, 1 warning
node --check: erfolgreich
```

Playwright-Dogfood:
- `Analysieren` auf `python/agent_server.py` zeigt echte Analyse-JSON sichtbar.
- `Reparieren` ohne Issue zeigt `Keine Issue-Beschreibung` statt Fake-Success.
- `Reparieren` mit Issue zeigt echten `proposal_only`-Response.
- `+ Neues Backup` legt real ein Backup an; Dogfood-Backups wurden danach per API wieder entfernt.
- Backup-Liste zeigt zeilenbezogene `Wiederherstellen`/`Löschen`-Buttons.
- Erster Klick schaltet auf `Restore bestätigen` bzw. `Löschen bestätigen`, ohne direkt Restore/Delete auszuführen.

---

## Evidence
- `dogfood-output/button-audit/02-code-buttons-real.png`
- `dogfood-output/button-audit/03-backup-buttons-real.png`
- `dogfood-output/button-audit/04-backup-arm-buttons.png`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** verbleibende Buttons auf Ausführungsziele/Projektflächen weiter dogfooden
