# EIDO-003 — Capability-Drift und falscher QUIC-Listener-Status in `/health`

- **ID:** `EIDO-003`
- **Titel:** `/health` und `/capabilities` nutzten uneinheitliche Capability-Quellen und behaupteten einen QUIC-Listener
- **Primärkategorie:** `fake`
- **Severity:** `S0`
- **Status:** `verified`
- **Bereich:** `runtime`
- **Surface:** `api`
- **Gefunden in Block:** `B, I`

---

## Claim
> Capability-Status und QUIC-Portzustand spiegeln die reale Runtime wider.

## Reality
Vor dem Fix:
- `/health` baute eine eigene hartcodierte Capability-Liste
- `/capabilities` leitete diese gleiche hartcodierte Liste nur durch
- `quic_port` stand immer auf `listening: true`
- obwohl der Python-Server keinen echten QUIC-Listener veröffentlichte

## Warum das problematisch ist
Das kombinierte zwei Produktlügen:
1. Capability-Wahrheit driftete vom eigentlichen Registry-Modell ab
2. Mesh-/Transportstatus behauptete Laufzeitfähigkeit ohne echte Bindung

---

## Evidence

### Quelle(n)
- `python/agent_server.py`
- `python/eidolon/core/capabilities.py`
- `GET /health`
- `GET /capabilities`

### Direkter Beleg vor Fix
```text
caps = [ ... hartcodierte Liste ... ]
"quic_port": {"listening": True, "port": QUIC_PORT}
```

### Reproduktion
1. `/capabilities` aufrufen
2. Antwort mit `build_default_capabilities()` vergleichen
3. `/health` prüfen: `quic_port.listening` war immer `true`

---

## Klassifikation

### Wahrheitstyp aktuell
- [x] derived_honest
- [ ] fake

### Produktauswirkung
- [x] Produktlüge / Vertrauensbruch
- [x] Capability-Wahrheit falsch

---

## Root Cause
`agent_server.py` nutzte eine doppelte, manuelle Capability-Quelle und einen hartcodierten Transportstatus statt realer oder explizit unavailable markierter Zustände.

## Fix Required
- [x] Code ändern
- [x] Test ergänzen
- [x] Runtime neu starten

## Konkrete Änderung
- `/health` nutzt jetzt `get_capability_registry().list()`
- `/capabilities` liefert damit die Registry-Form zurück
- `quic_port` ist jetzt ehrlich:
  - `listening: false`
  - `status: not_wired`
  - erklärendes `detail`

---

## Verifikation

### Pflichtchecks
- [x] Tests ergänzt
- [x] Live-Endpoint geprüft
- [x] Runtime neu gestartet

### Verifikationsbelege
```text
pytest:
test_capabilities_endpoint_uses_registry_shape
test_health_does_not_claim_quic_listener_when_not_wired
11 passed, 1 warning

Live /health:
"quic_port":{"listening":false,"status":"not_wired",...}

Live /capabilities:
enthält registry-basierte IDs wie browser.control und mesh.quic
```

### Done When
Capability- und Transportstatus dürfen nur aus der echten Quelle oder als explizit unavailable/not_wired erscheinen.

---

## Abschluss

- **Fix Commit / Änderung:** lokale Codeänderung in `agent_server.py`
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** echte QUIC-Runtime anbinden oder weiterhin bewusst unavailable halten
