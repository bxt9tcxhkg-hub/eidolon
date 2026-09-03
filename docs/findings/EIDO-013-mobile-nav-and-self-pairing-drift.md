# EIDO-013 — Mobile-Navigation und Self-Pairing waren unter echter Interaktion unehrlich

- **ID:** `EIDO-013`
- **Titel:** Mobile-Nav wurde vom Statusbadge blockiert; Pairing-Page behauptete Erfolg bei Self-Pairing
- **Primärkategorie:** `fake`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `mobile`, `mesh`, `pairing`, `ui`
- **Surface:** `web`
- **Gefunden in Block:** `D`

---

## Claim
> Mobile-Navigation und Pairing funktionieren auf echten kleinen Viewports korrekt.

## Reality
Unter echter mobiler Interaktion gab es zwei konkrete Brüche:

1. **Mobile-Navigation**
   - der feste Badge `#ws-status` lag über der unteren Mobile-Bar
   - auf dem `Mehr`-Button traf `elementFromPoint(...)` statt des Nav-Elements den Statusbadge
   - Ergebnis: Mobile-Navigation war real blockiert

2. **Self-Pairing**
   - die Pairing-Seite zeigte nach Klick auf `Verbinden` ein Erfolgs-UI
   - gleichzeitig blieben `/mesh/pairing/paired` und `/mesh/peers` leer
   - das System akzeptierte also einen inhaltlich ungültigen Self-Pairing-Pfad, obwohl nach außen kein realer Peer existierte

---

## Fix
- `python/eidolon/web/index.html`
  - `#ws-status` auf `pointer-events: none` gesetzt
  - Mobile-Lage des Badges oberhalb der Bottom-Bar und unterhalb des More-Sheets angepasst
- `python/eidolon/core/mesh_service.py`
  - Self-Pairing wird vor der Annahme explizit erkannt und mit klarer Fehlermeldung abgelehnt
- `python/agent_server.py`
  - `/mesh/pairing/accept` gibt den ehrlichen Service-Status direkt zurück

---

## Verifikation
```text
pytest: 24 passed, 1 warning
node --check: erfolgreich
```

Echte mobile Dogfood-Checks via Playwright:
- `elementFromPoint` über dem More-Button trifft jetzt wieder das Nav-Element statt `#ws-status`
- Klick auf `Mehr` öffnet das Sheet real
- Klick auf `Mesh & Geräte` funktioniert real auf mobilem Viewport
- Self-Pairing zeigt jetzt:
  - `✗ Dieses Gerät kann sich nicht mit sich selbst koppeln`
- `/mesh/pairing/paired` → `[]`
- `/mesh/peers` → `[]`
- testbedingt erzeugte Pending-Codes wurden nach der Verifikation wieder entfernt

---

## Evidence
- `dogfood-output/mobile-pairing/10-more-click-works.png`
- `dogfood-output/mobile-pairing/11-mobile-mesh-click-works.png`
- `dogfood-output/mobile-pairing/12-self-pair-rejected.png`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `medium`
- **Follow-up nötig:** Rollenwirkung und restliche Error-/Unavailable-Pfade weiter auditieren
