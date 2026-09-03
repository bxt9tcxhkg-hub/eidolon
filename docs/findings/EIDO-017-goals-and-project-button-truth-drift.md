# EIDO-017 — Ausführungsziel- und Projektflächen-Buttons waren nicht vertragswahr genug

- **ID:** `EIDO-017`
- **Titel:** Zielaktionen ignorierten erlaubte Übergänge; Revalidierung ließ erledigte Probleme als aktive/planned Ziele stehen; Projektbuttons hatten stille Error-Noops
- **Primärkategorie:** `fake`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `goals`, `workspaces`, `buttons`, `runtime-state`
- **Surface:** `web`, `api`, `persistence`
- **Gefunden in Block:** `next7`

---

## Claim
> Ausführungsziele und Projektflächen-Buttons sind echte, zustandswahr angebundene Produktaktionen.

## Reality
Es gab mehrere konkrete Driftpunkte:

1. **Zielbuttons ignorierten die Statusmaschine**
   - erledigte Ziele zeigten weiter `Starten`, `Erledigt`, `Löschen`
   - aktive Ziele zeigten nicht die wirklich erlaubten Übergänge wie `Pausieren`/`Fehlgeschlagen`
   - UI nutzte `PUT /autonomy/goals/{id}` statt den echten Transition-Endpunkt

2. **Zielstatus war kontaminiert**
   - dasselbe Problem existierte gleichzeitig als altes `done`-Ziel und als neues offenes Ziel
   - besonders sichtbar: `Blocker: Image-Generation` aktiv und erledigt zugleich
   - ebenso doppelte `TTS/STT`- und `Rust-Stubs`-Ziele

3. **Revalidierung erzeugte widersprüchliche Zustände**
   - `verify: resolved` konnte auf `planned` stehen bleiben, weil `planned → done` kein normaler manueller Übergang ist
   - dadurch zeigte die UI ein gelöstes Problem weiter als startbare Aufgabe

4. **Projektflächenbuttons hatten stille Fehlerpfade**
   - `submitProjectForm`, `submitTaskForm`, `deleteProject`, `deleteCurrentComposerElement`, `generateBrainstorm`, `acceptSuggestion` prüften `{ok:false}` nicht konsequent
   - Fehler konnten dadurch als Noop verschwinden oder als Erfolg wirken

---

## Fix
- `python/eidolon/web/index.html`
  - Zielkarten rendern Buttons jetzt aus `allowed_transitions`
  - erledigte/abgebrochene Ziele zeigen `Keine Aktionen`
  - Statuswechsel nutzt jetzt `POST /autonomy/goals/{id}/transition`
  - Ableitung, Zyklus und Revalidierung rendern echte JSON-Ergebnisse im UI
  - Zielstatistiken nutzen echte `active_count`/`done_count` aus der API statt nicht existente `active`/`done`-Felder

- `python/eidolon/core/autonomy_engine.py`
  - Revalidierung schließt `verify: resolved` Ziele jetzt terminal als `done`, auch wenn der normale manuelle Übergang das nicht erlauben würde
  - Begründung: Revalidierung ist Wahrheitskorrektur, kein manueller Button-Flow

- `python/eidolon/web/workspace-ui.js`
  - Projekt-/Element-/Brainstorm-/Delete-Flows prüfen `{ok:false}` konsequent
  - Fehler werden als UI-Fehler angezeigt statt still zu verschwinden

- Live-State bereinigt:
  - alte terminale Duplikate mit gleichem `problem_key` archiviert und entfernt
  - Backup: `data/backups/autonomy_goals_cleanup_20260825T225824Z/goals.json`

---

## Verifikation
```text
pytest: 29 passed, 1 warning
node --check: erfolgreich
```

Live/API:
- Ziele nach Cleanup/Revalidierung: 6 statt 9
- `Blocker: Image-Generation` nur noch offen/aktiv, nicht zugleich erledigt
- `Rust-Stubs` ist jetzt `done` + `verify: resolved`
- Stats: `6 Gesamt`, `1 Aktiv`, `2 Erledigt`

Playwright-Dogfood:
- Zielkarten zeigen nur erlaubte Aktionen
- erledigte Ziele zeigen `Keine Aktionen`
- `Aus Systemzustand ableiten` rendert echte Vorschlags-JSON
- `Prüfen & aufräumen` rendert echte Revalidierungs-JSON
- Projekt anlegen über UI funktioniert
- Element anlegen über UI funktioniert
- Element ohne Titel zeigt echten Fehler `Titel erforderlich`
- Dogfood-Projekt wurde wieder entfernt; final kein zusätzlicher Projekt-Testmüll

---

## Evidence
- `dogfood-output/goals-project-buttons/05-goals-final-truth.png`
- `dogfood-output/goals-project-buttons/08-project-element-buttons-real.png`
- `dogfood-output/goals-project-buttons/09-project-delete-armed.png`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** weitere Nebenflächen nur noch dort dogfooden, wo neue Buttons/Flows sichtbar werden
