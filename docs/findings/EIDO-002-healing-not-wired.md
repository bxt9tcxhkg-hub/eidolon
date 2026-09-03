# EIDO-002 — Healing-Endpunkt meldete `ok`, obwohl kein Runtime-Wiring existierte

- **ID:** `EIDO-002`
- **Titel:** `/healing/status` behauptete betriebsbereites Healing ohne Verdrahtung
- **Primärkategorie:** `fake`
- **Severity:** `S0`
- **Status:** `verified`
- **Bereich:** `healing`
- **Surface:** `api`
- **Gefunden in Block:** `B, H`

---

## Claim
> Self-Healing ist im Runtime-Betrieb aktiv und gesund.

## Reality
Vor dem Fix lieferte der Endpunkt stumpf:
```json
{"status":"ok","events":[],"last_event":null}
```
Obwohl `SelfHealingService` zwar als Code existiert, aber in `agent_server.py` nicht gestartet oder verdrahtet war.

## Warum das problematisch ist
Das war ein klassischer Produkt-Fake: grüner Gesundheitsstatus ohne echte Laufzeitfunktion.

---

## Evidence

### Quelle(n)
- `python/agent_server.py`
- `python/eidolon/core/healing.py`
- `GET /healing/status`

### Direkter Beleg vor Fix
```text
@app.get("/healing/status")
async def healing_status():
    return {"status": "ok", "events": [], "last_event": None}
```

### Reproduktion
1. `GET /healing/status`
2. Antwort ist immer `ok`
3. Codebasis prüfen: kein gestarteter `SelfHealingService` in der Runtime

---

## Klassifikation

### Wahrheitstyp aktuell
- [x] unavailable_explicit
- [ ] fake

### Produktauswirkung
- [x] Produktlüge / Vertrauensbruch
- [x] UI/API sagt etwas Falsches

---

## Root Cause
Der Endpunkt war hartcodiert und nicht an den realen Runtime-Zustand angebunden.

## Fix Required
- [x] Code ändern
- [x] Test ergänzen
- [x] Live-Endpoint prüfen

## Konkrete Änderung
- `python/agent_server.py`
  - `/healing/status` liefert jetzt ehrlich:
    - `status: not_wired`
    - `available: false`
    - erklärendes `detail`
  - `/health` meldet `self_healing` ebenfalls als `not_wired`

---

## Verifikation

### Pflichtchecks
- [x] Test ergänzt
- [x] Live-Endpoint geprüft
- [x] Runtime neu gestartet

### Verifikationsbelege
```text
pytest:
test_healing_status_is_honest_when_runtime_is_not_wired
11 passed, 1 warning

Live /healing/status:
{"status":"not_wired","available":false,...}
```

### Done When
Healing darf nur dann `ok` melden, wenn eine reale Verdrahtung und Laufzeitaktivität existiert.

---

## Abschluss

- **Fix Commit / Änderung:** lokale Codeänderung in `agent_server.py`
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** echtes SelfHealingService-Wiring oder bewusstes Belassen als unavailable
