# EIDO-012 — Settings-Flow und Elementeditor hatten unechte oder zu flache Bearbeitungspfade

- **ID:** `EIDO-012`
- **Titel:** Settings nutzten tote Modal-/Prompt-Pfade; Elementeditor blendete zentrale Felder aus
- **Primärkategorie:** `placeholder`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `ui`, `settings`, `project-model`
- **Surface:** `web`
- **Gefunden in Block:** `D`

---

## Claim
> Einstellungen und Projektelemente lassen sich in der Oberfläche sinnvoll und ehrlich bearbeiten.

## Reality
Vor dem Fix gab es zwei Drifts:
1. **Settings-Flow**
   - totes Settings-Modal mit `Speichern`
   - JS-Funktionen `saveSettings()` / `resetSettings()` nutzten Prompt-/Confirm-Pfade und teilweise nicht existente Endpunkte
2. **Elementeditor**
   - zentrale Felder wie `status`, `assigned_to` und `due_at` waren im Direkteditor nicht bearbeitbar
   - Typen `deliverable` und `milestone` fehlten trotz Backend-/Modellunterstützung in der UI-Auswahl

Dadurch wirkte die UI vollständiger, als sie es tatsächlich war.

---

## Fix
- `python/eidolon/web/index.html`
  - totes Settings-Modal entfernt
  - prompt-/confirm-basierte Settings-Funktionen entfernt
  - echte Reset-Buttons pro Settings-Bereich eingebaut (`/settings/{area}/reset`)
  - Elemente-Formular erweitert um:
    - `status`
    - `assigned_to`
    - `due_at`
    - zusätzliche Typen `deliverable`, `milestone`
- `python/eidolon/web/workspace-ui.js`
  - Direkteditor lädt/speichert die neuen Felder real

---

## Verifikation
```text
pytest: 23 passed, 1 warning
node --check: erfolgreich
```

Live:
- `/settings` weiterhin erreichbar und korrekt
- `/projects` bleibt leer nach Verifikation
- `/mesh/peers` bleibt leer und ehrlich

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** mobile und Pairing-Interaktionen weiterhin vollständig dogfooden
