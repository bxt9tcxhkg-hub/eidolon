# EIDO-004 — `/settings` unterschied Defaults nicht von explizit gesetzten Nutzerwerten

- **ID:** `EIDO-004`
- **Titel:** Settings lieferten Werte ohne Herkunftsmarker
- **Primärkategorie:** `placeholder`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `persistence`, `api`, `ui`
- **Surface:** `api`, `web`
- **Gefunden in Block:** `B, D, G`

---

## Claim
> Die gelieferten Einstellungen seien der reale aktuelle Nutzerzustand.

## Reality
Vor dem Fix lieferte `/settings` nur das zusammengeführte Objekt. Die Oberfläche konnte nicht erkennen, ob ein Wert:
- explizit vom Nutzer gesetzt wurde
- nur Default ist
- aus einem dynamischen Tab-Bereich stammt

Damit konnten Defaults wie bewusste Nutzerentscheidungen erscheinen.

---

## Fix
- `python/eidolon/core/settings_store.py`
  - speichert für Default-Bereiche nur explizite Abweichungen
  - liefert `get_all_with_meta()` und `get_area_with_meta()`
  - markiert jeden Wert mit `source: default|stored`
- `python/agent_server.py`
  - `/settings` und `/settings/{area}` liefern jetzt `settings_meta` und `source_counts`
  - Runtime nutzt den zentralen Shared Settings Store statt einer driftenden Duplikat-Implementierung
- `python/eidolon/web/index.html`
  - Settings-UI rendert Herkunftsbadges `standard` / `gesetzt`
- Vertragstests ergänzt

---

## Verifikation
```text
pytest: 16 passed, 1 warning
```

Live:
- `/settings` enthält `settings_meta`
- `/settings/ui` markiert `theme`, `density`, etc. explizit als `default`
- `source_counts` wird mitgeliefert

Datei-Zustand:
- `data/user/settings.json` enthält jetzt nur noch explizite Abweichungen und dynamische Bereiche statt eines komplett aufgeblähten Voll-Dumps

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
- **Follow-up nötig:** Nur falls Settings später inline editierbar gemacht werden sollen
