# EIDO-008 — Testlauf kontaminierte Live-Projektzustand

- **ID:** `EIDO-008`
- **Titel:** Vertragstest schrieb `Verifizierbares Projekt` in den Live-State und räumte nicht auf
- **Primärkategorie:** `contaminated`
- **Severity:** `S0`
- **Status:** `verified`
- **Bereich:** `persistence`, `tests`
- **Surface:** `api`, `web`
- **Gefunden in Block:** `D, G, I`

---

## Claim
> Live-Projekte repräsentieren echte Produktzustände.

## Reality
Der Test `test_project_suggestions_do_not_invent_review_items_when_no_gap_exists()` legte echte Projekte im Live-Store an und restaurierte den Zustand nicht. Dadurch erschienen mehrere Testartefakte live in `/projects` und in der Oberfläche „Projektflächen“.

Gefundene Artefakte:
- vier Projekte mit Titel `Verifizierbares Projekt`
- identische Testbeschreibung und Testelemente

## Warum das kritisch ist
Das ist kein kosmetischer Fehler, sondern Live-State-Kontamination durch Testcode.

---

## Fix
1. Test gehärtet:
   - `tests/test_web_ui_contracts.py`
   - sichert `data/user/projects.json` vor dem Test
   - restauriert den Originalzustand im `finally`
2. Bereits kontaminierten Live-State bereinigt:
   - Backup angelegt:
     `C:/Users/muham/eidolon/data/backups/projects_cleanup_20260825T130156Z/projects.json`
   - vier Testprojekte aus `data/user/projects.json` entfernt

## Verifikation
```text
Live /projects:
{"projects":[]}

Live UI Projektflächen:
"Keine Projekte"

pytest: 14 passed, 1 warning
```

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
