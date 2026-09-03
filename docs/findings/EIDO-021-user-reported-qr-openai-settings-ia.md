# EIDO-021 — Nutzerberichtete Flows: QR-Pairing, OpenAI-Verbindung, Einstellungen und Informationsarchitektur

- **ID:** `EIDO-021`
- **Titel:** Handy-QR koppelte Eidolon mit sich selbst, Einstellungen waren read-only, OpenAI-Verbindung war nicht ehrlich bedienbar, Seitennavigation war zu technisch/zerstückelt
- **Status:** `verified`
- **Severity:** `S1`
- **Bereiche:** `mesh`, `llm`, `settings`, `navigation`, `mobile`, `truth-hardening`

---

## Nutzer-Symptome
- Handy scannt QR-Code und bekommt: `Dieses Gerät kann sich nicht mit sich selbst koppeln`.
- OpenAI/OAuth-Verbindung ist nicht möglich.
- Einstellungen lassen sich nicht ändern.
- `Systempflege` und `Ausführung` sind in Zweck und Informationsgehalt unklar.
- Aufteilung `Hauptbereiche`/`System` wirkt verwirrend und zu stark gesplittet.

---

## Root Cause
1. **QR-Pairing:** Der QR-Code enthielt Eidolons eigene Identität. Die mobile Pairing-Seite akzeptierte denselben Code ohne eigene Browser-/Handy-Geräteidentität zu senden. Der Server erkannte korrekt Self-Pairing und lehnte ab — der QR-Flow war also falsch modelliert.
2. **OpenAI:** `llm_backend` konnte nur Ollama ausführen. OpenAI wurde in Settings/Identity erwähnt, war aber nicht als realer Providerpfad inklusive Credential-Status angebunden. OAuth wurde nicht implementiert und durfte nicht als vorhanden erscheinen.
3. **Einstellungen:** Settings renderten nur Werte und Herkunfts-Badges; es gab Reset-Buttons, aber keine speicherbaren Eingabefelder.
4. **Informationsarchitektur:** Sidebar-Gruppen waren technisch (`Hauptbereiche`/`System`) und Seiten wie `Systempflege`/`Ausführung` erklärten nicht, warum sie existieren.
5. **Config-Drift:** `settings.json` und `python/data/llm_config.json` konnten auseinanderlaufen; Runtime-Provider war dadurch nicht zwingend identisch mit den sichtbaren Settings.

---

## Fix
- QR-Pairing:
  - Mobile Pairing-Seite erzeugt/stabilisiert eine Browser-Geräteidentität im lokalen Browser.
  - `POST /mesh/pairing/accept` unterscheidet Desktop-Self-Pairing von echtem Browser-/Handy-Pairing.
  - Handy/Browser wird als `browser_device` gespeichert, Self-Pairing bleibt blockiert.
- OpenAI:
  - OpenAI ist als echter API-Key-Providerpfad angebunden.
  - `/llm/connection` zeigt Credential-Status ohne Key-Wert.
  - `/llm/openai/api-key` speichert/entfernt den Key-Wert, gibt ihn nie zurück.
  - UI sagt explizit: OAuth ist hier nicht angebunden; Verbindung läuft per API-Key.
- Einstellungen:
  - Settings rendern echte Inputs/Selects für Netzwerk, KI, Autonomie, Datenschutz und UI.
  - Jede Area hat `Änderungen speichern`, echte `POST /settings/{area}`-Anbindung und Fehlerbehandlung.
- LLM-Config:
  - Runtime-LLM wird beim Start aus dem SettingsStore synchronisiert.
- Informationsarchitektur:
  - Sidebar umgruppiert zu `Arbeiten`, `Verbindungen & Zustand`, `Konfiguration`.
  - `Ausführung` heißt jetzt `Autonomie-Ziele`.
  - `Systempflege` heißt jetzt `Code-Reparatur`.
  - Seiten `Autonomie-Ziele` und `Code-Reparatur` enthalten kurze Zweckkarten.

---

## Verifikation
```text
python -m pytest -q      -> 36 passed, 1 warning
cargo check --workspace  -> Finished
node --check             -> alle Inline-Skripte + workspace-ui.js OK
```

Live-Dogfood:
- Self-Pairing bleibt blockiert.
- Browser-/Handy-Pairing über QR-Code wird akzeptiert.
- Settings speichern echte LLM-Werte.
- OpenAI-Status zeigt `oauth_supported: false`, `auth_method: api_key`.
- Navigation enthält die neuen Gruppen und Labels.
- `Autonomie-Ziele` und `Code-Reparatur` erklären ihren Zweck.

Cleanup:
- Dogfood-Pairing entfernt.
- Dogfood-Settings zurückgesetzt.
- Dogfood-OpenAI-Key entfernt.
- Nach Neustart: `/mesh/pairing/paired -> []`, `/projects -> []`, `/backups -> []`, Settings/Runtime wieder `ollama`.

---

## Evidence
- `dogfood-output/user-reported-flows/04-reworked-sidebar-ia.png`
- `dogfood-output/user-reported-flows/05-editable-settings-openai-truth.png`
- `dogfood-output/user-reported-flows/06-code-repair-purpose.png`

---

## Schluss
Die Nutzerkritik war berechtigt: Der vorherige Abschluss war zu optimistisch. Die genannten Punkte waren echte Restlücken und sind jetzt behoben/verifiziert.
