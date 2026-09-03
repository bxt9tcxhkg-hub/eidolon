# EIDO-018 — Tiefe Projekt-/Canvas-Interaktionen hatten unvollständige Fehler- und Persistenzwahrheit

- **ID:** `EIDO-018`
- **Titel:** Canvas-Create ignorierte Position/Parent; Link-/Hierarchie-Flows hatten stille Persistenzfehler
- **Primärkategorie:** `fake`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `project-workspaces`, `canvas`, `buttons`, `direct-manipulation`
- **Surface:** `web`, `api`
- **Gefunden in Block:** `next8`

---

## Claim
> Projektflächen-Buttons und Canvas-Direktinteraktionen sind real verdrahtet, speichern sichtbare Semantik und zeigen Fehler ehrlich.

## Reality
Beim tiefen Dogfood der Projektfläche gab es drei konkrete Lücken:

1. **Element-Erzeugung über API verlor Canvas-Position/Parent**
   - `POST /projects/{project_id}/elements` nahm zwar UI-Payloads entgegen, gab `position`/`parent_id` aber nicht an das Modell weiter.
   - Ergebnis: programmatisch oder über Canvas erzeugte Elemente konnten bei `{x:120,y:120}` trotzdem bei `{x:0,y:0}` landen.
   - Das machte direkte Manipulation und Dogfood-Klickziele unehrlich.

2. **Link-/Hierarchie-Canvas-Flows hatten optimistische lokale Mutation**
   - `addDependency()` und `assignHierarchy()` änderten lokalen State und feuerten API-Calls ohne `{ok:false}`-Prüfung/Rollback.
   - Ein fehlgeschlagener Persistenzpfad hätte im Canvas Erfolg angezeigt, obwohl Backend-State nicht stimmt.

3. **Projektflächen-Buttons hatten noch stille Noop-Risiken**
   - Projekt-/Element-/Brainstorm-Flows wurden bereits gehärtet, aber Canvas-Semantik musste zusätzlich abgesichert werden.

---

## Fix
- `python/agent_server.py`
  - `add_element()` persistiert jetzt auch:
    - `position`
    - `parent_id`
- `python/eidolon/web/workspace-ui.js`
  - `addDependency()`:
    - merkt vorherige Dependencies
    - prüft `{ok:false}`
    - rollt lokale Änderung bei Fehler zurück
    - lädt Projekt nach erfolgreichem Persistieren neu
  - `assignHierarchy()`:
    - merkt vorherige `parent_id`
    - prüft `{ok:false}`
    - rollt lokale Änderung bei Fehler zurück
    - lädt Projekt nach erfolgreichem Persistieren neu
- Contract-Test ergänzt für Position/Parent und Canvas-Fehlerpfade.

---

## Verifikation
```text
pytest: 30 passed, 1 warning
node --check: erfolgreich
```

Playwright/API-Dogfood:
- Temporäres Projekt erstellt
- zwei Elemente mit echten Canvas-Positionen erstellt:
  - `{x:120,y:120}`
  - `{x:460,y:260}`
- Link-Modus ausgeführt:
  - Dependency wurde im Backend persistiert
- Hierarchie-Modus ausgeführt:
  - `parent_id` wurde im Backend persistiert
- Projektstats zeigten 2 Elemente
- Dogfood-Projekt danach entfernt; final kein zusätzlicher Projekt-Testmüll

---

## Evidence
- `dogfood-output/deep-project-interactions/02-canvas-link-hierarchy-real.png`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** Weitere neue Projekt-/Canvas-Controls bei Auftauchen weiter dogfooden
