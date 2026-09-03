# EIDO-022 — Mobile Pairing endete nach Erfolg ohne echte Interaktion

- **ID:** `EIDO-022`
- **Titel:** QR-Pairing sagte „verbunden“, ließ das Handy danach aber nicht mit Eidolon interagieren
- **Status:** `verified`
- **Severity:** `S1`
- **Bereiche:** `mesh`, `mobile`, `chat`, `truth-hardening`

---

## Nutzer-Symptom
Nach dem Scannen des QR-Codes zeigte das Handy:

> Dieses Gerät ist mit Eidolon verbunden

Danach passierte nichts. Es gab keine Eingabe, keinen Chat, keine nächste Aktion und keine echte Interaktionsfläche.

---

## Root Cause
Der vorige Fix machte das Pairing zwar technisch erfolgreicher, aber nur als Zustandsmutation. Die mobile Pairing-Seite hatte nach `data.ok` ausschließlich Success-Text und Buttonzustand:

- Status wurde auf erfolgreich gesetzt.
- Button wurde auf `Verbunden` gesetzt.
- Es wurde keine Folgefläche geöffnet.
- Es gab keine echte Nachricht-/Chat-Aktion vom Handy aus.

Damit war der neue Erfolg selbst ein Placebo: verbunden wurde ein Gerät, aber die UI bot keine Nutzung.

---

## Fix
Die QR-Pairing-Seite enthält nach erfolgreichem Pairing jetzt eine echte Interaktionsfläche:

- Abschnitt `Mit Eidolon schreiben`
- Texteingabe `#mobileMessage`
- Button `Senden`
- echter API-Aufruf an `POST /chat`
- `source: mobile:<browser-peer-id>` für nachvollziehbare Herkunft
- echte Antwort oder echter Fehler wird in `#reply` gerendert

Kein Fake-Fallback: Wenn der LLM-Provider nicht erreichbar ist, zeigt die mobile Seite die echte Fehlermeldung statt so zu tun, als hätte Eidolon geantwortet.

---

## Verifikation
```text
python -m pytest -q      -> 36 passed, 1 warning
cargo check --workspace  -> Finished
node --check             -> Inline-Skripte + workspace-ui.js OK
```

Live-Dogfood auf mobilem 390px-Viewport:

1. Neues Pairing erzeugt.
2. Pairing-Seite geöffnet.
3. `Verbinden` geklickt.
4. Erfolg angezeigt: `Dieses Gerät ist mit Eidolon verbunden`.
5. Interaktionsfläche wurde sichtbar.
6. Nachricht `Antworte nur mit OK.` gesendet.
7. Echte `/chat`-Antwort erhalten: `OK.`
8. Dogfood-Interaction-Log und temporäres Pairing wieder auf vorherigen Zustand zurückgesetzt.

---

## Evidence
- `dogfood-output/mobile-pairing-interaction/01-before-connect.png`
- `dogfood-output/mobile-pairing-interaction/02-after-message.png`

---

## Schluss
Die Nutzerkritik war berechtigt: „Verbunden“ ohne anschließende Bedienmöglichkeit war funktional nicht ausreichend. Der Flow endet jetzt nicht mehr im Success-Dead-End, sondern öffnet eine echte Chat-Interaktion mit Eidolon.
