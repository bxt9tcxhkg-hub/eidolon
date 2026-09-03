# EIDO-007 — Chat-UI hatte einen Fake-Success-Fallback

- **ID:** `EIDO-007`
- **Titel:** Chat zeigte `Antwort erhalten`, wenn die API keine echte Modellantwort lieferte
- **Primärkategorie:** `fake`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `ui`
- **Surface:** `web`
- **Gefunden in Block:** `D, H`

---

## Claim
> Der Chat habe eine echte Assistant-Antwort geliefert.

## Reality
Vor dem Fix stand im Frontend:
```javascript
chatMessages.push({ role: 'assistant', content: r.response || r.message || 'Antwort erhalten' });
```
Wenn also keine echte Modellantwort vorhanden war, konnte die UI trotzdem eine positive Scheinantwort anzeigen.

## Fix
- `python/eidolon/web/index.html`
  - `r.ok === false` → expliziter Fehlertext
  - leere/missing `response` → `Fehler: Keine Modellantwort erhalten`
  - kein Success-Placebo mehr
- Vertragstest ergänzt

## Verifikation
```text
pytest: 14 passed, 1 warning
```

Quellvertrag:
- `'Antwort erhalten'` kommt im Frontend nicht mehr vor
- ehrlicher Fehlerpfad ist vorhanden

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
