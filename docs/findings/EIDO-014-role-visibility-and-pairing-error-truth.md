# EIDO-014 — Rollenwirkung war im UI zu flach, und Pairing-Fehler wurden als Erfolg getoastet

- **ID:** `EIDO-014`
- **Titel:** Identität zeigte nur Rollenzählung; Mesh-UI meldete Pairing-Fehler als Erfolg
- **Primärkategorie:** `fake`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `roles`, `identity`, `mesh`, `error-paths`
- **Surface:** `web`, `api`
- **Gefunden in Block:** `E`, `H`

---

## Claim
> Rollenwirkung und Fehlerpfade werden in UI und API ehrlich gezeigt.

## Reality
Es gab zwei getrennte Unehrlichkeiten:

1. **Rollenwirkung im UI war zu flach**
   - `/identity` zeigte nur Zählwerte (`active_role_count`, `defined_role_count`)
   - die Oberfläche machte nicht sichtbar, *welche* Rolle aktiv wirkt und *welche* Vorlagen nur definiert sind
   - dadurch blieb die eigentliche Organisationswirkung im UI verborgen

2. **Pairing-Fehlerpfad im Mesh-UI war falsch**
   - `acceptPairing()` zeigte nach `/mesh/pairing/accept` immer `Verbunden!`
   - auch dann, wenn die API bereits `{ok:false, error: ...}` zurückgab
   - dadurch wurde ein echter Fehler als Erfolg präsentiert

---

## Fix
- `python/agent_server.py`
  - `/identity` liefert jetzt zusätzlich:
    - `active_roles`
    - `defined_roles`
  - jeweils mit echten Rollenattributen statt nur Zählwerten
- `python/eidolon/web/index.html`
  - Produktidentität rendert jetzt:
    - **Aktiv wirksame Rollen**
    - **Definierte Vorlagen**
    - inkl. Sichtbarkeit, Freigabepflicht und Nutzerbeschreibung
  - `acceptPairing()` prüft jetzt `r.ok === false` und zeigt dann einen Fehler-Toast statt Erfolgs-Toast

---

## Verifikation
```text
pytest: 25 passed, 1 warning
node --check: erfolgreich
```

Live:
- `/identity` enthält jetzt echte `active_roles` und `defined_roles`
- Produktidentität rendert diese real im UI
- Self-Pairing im Mesh-UI zeigt jetzt als Notice:
  - `Dieses Gerät kann sich nicht mit sich selbst koppeln`
  - statt falschem `Verbunden!`
- Pending-Codes aus der Verifikation wurden wieder entfernt

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** restliche Unavailable-/Error-Pfade außerhalb von Mesh/Identity weiter prüfen, falls neue Flächen dazukommen
