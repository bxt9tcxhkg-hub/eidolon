# EIDO-015 — Hauptscreen hatte stillen Leerraum und Skills-Liste blieb auf Ladezustand hängen

- **ID:** `EIDO-015`
- **Titel:** Chat-Startfläche war leer ohne ehrlichen Zustand; Skills-Liste blieb trotz echter Daten auf `Lade Skills...`
- **Primärkategorie:** `placeholder`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `main-screen`, `chat`, `skills`, `ui`
- **Surface:** `web`
- **Gefunden in Block:** `D`

---

## Claim
> Der Hauptscreen zeigt einen ehrlichen Startzustand, und die Skills-Fläche repräsentiert den realen Runtime-Stand.

## Reality
Es gab zwei zu flache bzw. inkonsistente Hauptflächenzustände:

1. **Chat-Startfläche**
   - `#chat-messages` war initial einfach leer
   - kein Fehler, aber auch keine ehrliche Erklärung, dass noch kein Gesprächskontext existiert
   - Ergebnis: stiller schwarzer Leerraum statt belastbarer Startzustand

2. **Skills-Fläche**
   - `/skills` lieferte echte Daten
   - `skills-summary` wurde befüllt
   - `skills-list` blieb aber auf `Lade Skills...`
   - Ergebnis: derselbe Bereich zeigte gleichzeitig echte Daten und einen falschen Ladezustand

---

## Fix
- `python/eidolon/web/index.html`
  - `renderChat()` zeigt jetzt bei leerem Chat einen expliziten ehrlichen Startzustand
  - `renderChat()` wird beim Initialisieren sofort aufgerufen
  - `loadSkills()` befüllt jetzt sowohl:
    - `skills-summary`
    - als auch `skills-list`
  - Fehler-/Leerfälle werden ebenfalls in beiden Zielbereichen konsistent gerendert

---

## Verifikation
```text
pytest: 26 passed, 1 warning
node --check: erfolgreich
```

Playwright-Dogfood:
- Hauptscreen zeigt jetzt:
  - `Noch kein Gesprächskontext. Schreibe oben deine erste Nachricht, damit Eidolon einen realen Arbeitskontext aufbauen kann.`
- Skills-Fläche zeigt jetzt reale Skills statt `Lade Skills...`

---

## Evidence
- `dogfood-output/mainscreen-audit/04-home-chat-empty-honest.png`
- `dogfood-output/mainscreen-audit/05-skills-list-real.png`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** Hauptscreen und weitere Nebenflächen weiter auf verbleibende semantische Flachheit prüfen
