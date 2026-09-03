# EIDO-024 — Geräte-Paarung muss über UI/API aufgehoben werden können

- **ID:** `EIDO-024`
- **Titel:** Gekoppelte Handy-/Browser-Geräte konnten nicht sichtbar entkoppelt werden
- **Status:** `verified`
- **Severity:** `S1`
- **Bereiche:** `mesh`, `mobile`, `settings`, `truth-hardening`

---

## Nutzerfrage
> wie kann ich die paarung der geräte wieder aufheben?

Vor diesem Fix war die ehrliche Antwort: nicht sauber über die UI. Es gab sichtbare gekoppelte Geräte, aber keinen produktiven Entkoppeln-Flow.

---

## Root Cause
- `/mesh/pairing/paired` konnte gekoppelte Geräte auflisten.
- Es gab aber keinen passenden Delete-/Unpair-Endpunkt.
- Die Web-/Mobile-UI zeigte Peers ohne echte Entfernen-Aktion.
- Manuelles Bearbeiten von `data/mesh/pairings.json` wäre keine akzeptable Nutzerlösung und wäre als Produktflow ein Placebo.

---

## Fix
- `MeshPairing.unpair(peer_id)` entfernt eine Kopplung dauerhaft aus dem Pairing-State.
- `MeshService.unpair_peer(peer_id)` validiert echte vorhandene Kopplungen und meldet `ok:false`, wenn das Gerät nicht existiert.
- Neuer echter API-Endpunkt:
  - `DELETE /mesh/pairing/paired/{peer_id}`
- Mesh-UI lädt jetzt echte Discovery-Peers plus gespeicherte Pairings.
- Für gekoppelte Geräte erscheint ein Button `Entkoppeln`.
- Entkoppeln ist als sichtbarer Zwei-Klick-Flow umgesetzt:
  - erster Klick: `Entkoppeln bestätigen`
  - zweiter Klick: echter `DELETE`-Call
- Wenn das aktuell genutzte mobile Gerät entkoppelt wird, wird auch `localStorage.eidolon-paired-device` entfernt, damit das Handy nicht weiter als gekoppelt markiert bleibt.

---

## Verifikation
```text
python -m pytest -q      -> 38 passed, 1 warning
node --check             -> Inline-Skripte + workspace-ui.js OK
cargo check --workspace  -> erfolgreich
```

Live-Dogfood:
1. Temporäres Gerät `Dogfood-Unpair-Device` gekoppelt.
2. Mobile Root-UI auf `/#mesh` geöffnet.
3. `Entkoppeln`-Button für das gekoppelte Gerät sichtbar.
4. Erster Klick armte die Aktion: `Entkoppeln bestätigen`.
5. Zweiter Klick rief `DELETE /mesh/pairing/paired/{peer_id}` auf.
6. Gerät verschwand aus der UI und aus `/mesh/pairing/paired`.
7. Dogfood-State wurde auf den Vorzustand zurückgesetzt.

---

## Evidence
- `dogfood-output/unpair-flow/01-mesh-with-unpair-button.png`
- `dogfood-output/unpair-flow/02-unpair-armed.png`
- `dogfood-output/unpair-flow/03-unpaired-removed.png`

---

## Schluss
Die Kopplung kann jetzt über die normale Eidolon-UI aufgehoben werden. Keine manuelle JSON-Bearbeitung, kein Fake-Button, kein stiller Erfolg.
