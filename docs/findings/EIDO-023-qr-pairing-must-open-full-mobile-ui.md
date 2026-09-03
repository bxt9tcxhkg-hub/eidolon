# EIDO-023 — QR-Pairing muss in die echte mobile Eidolon-UI führen

- **ID:** `EIDO-023`
- **Titel:** Pairing-Erfolg führte nur zu einer Sonderseite statt zur vollständigen Mobile-App-Shell
- **Status:** `verified`
- **Severity:** `S1`
- **Bereiche:** `mobile`, `mesh`, `chat`, `navigation`, `truth-hardening`

---

## Nutzer-Symptom
Nach dem QR-Scan meldete die Seite korrekt:

> Dieses Gerät ist mit Eidolon verbunden

Die danach sichtbare Seite war aber nicht die Mobile UI, sondern nur eine minimale Pairing-Folgeseite mit Chatfeld.

---

## Root Cause
Der vorige Fix beendete das Success-Dead-End, ersetzte es aber durch eine neue Sonderfläche. Das war weiterhin nicht der besprochene Produktzustand:

- Pairing-Seite blieb eine isolierte Einwegseite.
- Mobile Bottom Navigation wurde nicht genutzt.
- Status, Projekte, Ziele, Einstellungen, Mesh, Sicherungen und Stabilität waren vom Handy aus nicht als echte App-Shell erreichbar.
- Der gekoppelte Gerätezustand war nicht in der normalen Mobile UI sichtbar.

---

## Fix
- Die Pairing-Seite koppelt das Browser-/Handy-Gerät weiterhin real.
- Nach erfolgreicher Kopplung speichert sie lokal `eidolon-paired-device` und leitet direkt weiter nach `/#chat`.
- Die Root-App initialisiert Hash-Routing und öffnet die echte Mobile App-Shell.
- Die echte Mobile UI zeigt ein Banner, wenn das lokale Gerät in `/mesh/pairing/paired` wirklich vorhanden ist.
- Chat-Nachrichten aus der Mobile UI werden mit `source: mobile:<peer-id>` an `/chat` gesendet.
- Die isolierte Pairing-Chatfläche wurde entfernt.

---

## Verifikation
```text
python -m pytest -q      -> 37 passed, 1 warning
node --check             -> Inline-Skripte + workspace-ui.js OK
cargo check --workspace  -> erfolgreich
```

Live-Mobile-Dogfood:
1. Pairing-Code erzeugt.
2. Mobile Pairing-Seite geöffnet.
3. `Verbinden` geklickt.
4. Weiterleitung nach `/#chat` erfolgte.
5. Mobile Bottom-Bar war sichtbar.
6. Chat-Panel der normalen App war sichtbar.
7. Banner zeigte: `Dieses Handy ist gekoppelt`.
8. Nachricht im normalen Mobile-Chat gesendet.
9. `/chat` lieferte echte Antwort oder echten Fehler; im Lauf kam eine echte Antwort.
10. Dogfood-Interaction-Log und temporäres Pairing wurden auf den Vorzustand zurückgesetzt.

---

## Evidence
- `dogfood-output/mobile-pairing-full-ui/01-pairing-entry.png`
- `dogfood-output/mobile-pairing-full-ui/02-redirected-full-mobile-ui.png`
- `dogfood-output/mobile-pairing-full-ui/03-full-mobile-chat-after-pairing.png`

---

## Schluss
Der QR-Flow endet jetzt nicht mehr in einer Pairing-Sonderseite. Er koppelt das Gerät und öffnet danach die vollständige responsive Eidolon-App-Shell mit mobilem Gerätestatus.
