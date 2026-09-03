# EIDO-011 — Mesh zeigte Demo-/Self-Peer als reale Verbindung

- **ID:** `EIDO-011`
- **Titel:** Mesh-Peers enthielten Demo-Daten und Self-Pair-Kontamination
- **Primärkategorie:** `fake`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `mesh`, `persistence`, `ui`
- **Surface:** `api`, `web`
- **Gefunden in Block:** `D, G, H`

---

## Claim
> Die Mesh-Ansicht zeigt reale bekannte oder verbundene Geräte.

## Reality
Vor dem Fix bestanden zwei Wahrheitsdrifts:
1. `MeshService.scan_peers()` injizierte einen festen Demo-Peer:
   - `Eidolon-Demo-Peer`
   - `192.168.1.100`
2. `data/mesh/pairings.json` enthielt eine Self-Pair-Kontamination mit demselben Gerät/Schlüssel wie der lokale Runtime-Knoten.

Damit zeigte `/mesh/peers` scheinbar reale Gegenstellen, obwohl keine echte externe Peer-Verbindung vorlag.

---

## Fix
- `python/eidolon/core/mesh_service.py`
  - Demo-Peer-Injektion entfernt
  - Scan kombiniert jetzt nur noch reale Discovery-Peers und echte gespeicherte Pairings
  - Self-Pairings werden aus sichtbaren Peer-Listen gefiltert
- `python/eidolon/web/index.html`
  - Mesh-Liste zeigt jetzt Status ehrlich über `status`/`paired` statt über ein nicht existentes `connected`-Flag
  - globaler WS-Status unten rechts wird aus `/health` abgeleitet statt dauerhaft `Verbinde...` zu behaupten
- Persistenz bereinigt
  - Backup: `data/backups/mesh_pairings_cleanup_20260825T155837Z/pairings.json`
  - kontaminiertes Self-Pair aus `data/mesh/pairings.json` entfernt

---

## Verifikation
```text
pytest: 21 passed, 1 warning
node --check: erfolgreich
```

Live:
- `/mesh/peers` → `{"peers":[]}`
- `/mesh/pairing/paired` → `{"ok":true,"paired":[]}`
- `/mesh/status` → `peers: 0`, `paired: 0`
- `/health` bleibt ehrlich `ok_with_limits`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
- **Follow-up nötig:** Pairing-Flow UI unter echter Geräteverbindung noch vollständig dogfooden
