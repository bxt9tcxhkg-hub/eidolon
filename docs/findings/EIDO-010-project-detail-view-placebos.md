# EIDO-010 — Projektansicht bot echte View-Auswahl an, lieferte aber nur Scheinvarianten

- **ID:** `EIDO-010`
- **Titel:** Board/Timeline/Liste/Hierarchie waren als Produktfläche sichtbar, aber nicht real verdrahtet
- **Primärkategorie:** `placebo`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `ui`, `workspace`, `project-model`
- **Surface:** `web`
- **Gefunden in Block:** `D, E`

---

## Claim
> Die Projektfläche bietet echte Ansichten für Canvas, Board, Timeline, Liste und Hierarchie.

## Reality
Vor dem Fix war die Sichtauswahl teilweise Scheinfunktion:
- `board`, `timeline` und `list` landeten alle in derselben generischen Listenansicht
- der Canvas-Modus `hierarchy` war sichtbar, aber funktional nicht umgesetzt
- die UI behauptete damit semantische Arbeitsweisen, die nicht wirklich existierten

---

## Fix
- `python/eidolon/web/workspace-ui.js`
  - echte Renderer ergänzt:
    - `renderBoardView()`
    - `renderTimelineView()`
    - `renderListView()`
  - `switchView()` verdrahtet die Ansichten jetzt real getrennt
  - `assignHierarchy(childId, parentId)` ergänzt
  - Hierarchie-Modus im Canvas verdrahtet
  - Parent-Child-Kanten werden im Canvas sichtbar als gestrichelte grüne Linien gerendert
  - Projektstatistik im Detailkopf ergänzt
- `python/eidolon/web/index.html`
  - Elemente-Kopf bekam dynamischen Titel
  - Produktidentität zeigt jetzt auch Rollenwahrheit (`Aktive Rollen`, `Definierte Vorlagenrollen`, `Rollentypen`)
- Verträge erweitert

---

## Verifikation
```text
pytest: 18 passed, 1 warning
node --check: erfolgreich
```

Live verifiziert:
- Projekt live angelegt, Elemente mit `due_at`, `dependencies` und `parent_id` erzeugt
- API bestätigte reale Verdrahtung:
  - `updated_parent`: gesetzt
  - `updated_dependencies`: gesetzt
- Testprojekt nach der Verifikation wieder entfernt
- `/projects` wieder bereinigt

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** vollständige visuelle Dogfood-Prüfung der Projektansicht/Canvas-Interaktion unter echter Bedienung
