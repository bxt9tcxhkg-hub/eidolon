# EIDO-020 — Offene Restblöcke ohne Placebo/Fake geschlossen

- **ID:** `EIDO-020`
- **Titel:** Rust-Warnungen, Healing-Drahtung, Skills-Mutationen, Rollenaktivierung und Mobile-Restflächen waren noch nicht vollständig wahrheitsgehärtet
- **Primärkategorie:** `truth-hardening`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `runtime`, `healing`, `roles`, `skills`, `mobile`, `contracts`
- **Surface:** `web`, `api`, `rust`, `persistence`
- **Gefunden in Block:** `final-open-blocks`

---

## Claim
> Die verbliebenen offenen Blöcke sind entweder echt implementiert oder ehrlich als begrenzt markiert — ohne Placebo, Fake, Platzhalter oder Halluzination.

## Reality
Beim Abschlussaudit gab es noch konkrete Restlücken:

1. **Rust-Reifegrad**
   - `cargo check --workspace` lief zwar durch, aber mit mehreren `unused import`-Warnungen.
   - Rust-Health meldete Mesh/QUIC pauschal `Ok`, obwohl der HealthMonitor keinen echten Listener-/Transport-Probe hatte.

2. **Healing / Recovery**
   - Python-UI und `/healing/status` sagten `not_wired`, obwohl `SelfHealingService` existierte.
   - Es gab keinen echten manuellen UI-/API-Check-Flow.

3. **Skills-Endpunkte**
   - `/skills/enabled` lieferte leer.
   - Enable/Disable/Toggle/Priority antworteten Erfolg, ohne den Runtime-State wirklich zu ändern.

4. **Rollen-Laufzeitwirkung**
   - Die Anzeige war bereits ehrlich, aber die API erlaubte noch riskante dauerhafte Aktivierung von `ephemeral_only`-Rollen.
   - `eidolon-core` konnte nicht sauber als unlösbare Hauptrolle geschützt werden.

5. **Mobile-Restflächen**
   - Alle Tabs waren sichtbar, aber der neue Healing-Button lag mobil außerhalb der echten Viewport-Breite und war nicht zuverlässig klickbar.

---

## Fix
- Rust:
  - ungenutzte Imports entfernt
  - Rust-Health meldet Mesh/QUIC jetzt `Unknown` mit Begründung statt Fake-`Ok`, solange kein Probe verdrahtet ist
- Healing:
  - `SelfHealingService` wird per FastAPI-Lifespan gestartet/gestoppt
  - registrierte Checks: `runtime`, `backups`, `capabilities`, `certificates`
  - `/healing/status` gibt echten Running-/Check-State zurück
  - `/healing/check` führt einen echten Check-Zyklus aus
  - Web-UI zeigt registrierte Checks, Check-Zähler, Fehlerzähler und letztes Event
  - Button `Check ausführen` ruft echte API auf
- Skills:
  - `/skills/enabled` zeigt echte aktivierte Builtins
  - Enable/Disable/Toggle/Priority mutieren den Runtime-State oder melden `ok:false`
- Rollen:
  - `ephemeral_only`-Rollen dürfen nicht dauerhaft als `active` gespeichert werden
  - Aktivierung zustimmungspflichtiger Rollen verlangt `approved_by_user=true`
  - `eidolon-core` ist als direkte Hauptrolle vor Löschung geschützt
- Mobile:
  - Main-Layout ist jetzt mobil viewport-wahr (`width:100%`, `box-sizing:border-box`, kein Horizontal-Overflow)
  - Card-Header/Actions umbrechen mobil; Healing-Button liegt sichtbar/klickbar im Viewport

---

## Verifikation
```text
python -m pytest -q        -> 33 passed, 1 warning
cargo check --workspace    -> Finished, keine Warnings
node --check               -> alle Inline-Skripte + workspace-ui.js OK
```

Live/API:
- `/healing/status` -> `running`, `available: true`, Checks registriert
- `/healing/check` -> echter Check-Zyklus mit erfolgreichen Checks
- `/health.components.self_healing` -> `running`
- `/skills/chat/disable` entfernt `chat` aus `/skills/enabled`
- `/skills/chat/enable` fügt `chat` wieder hinzu
- unbekannter Skill -> `ok:false`
- `DELETE /bots/roles/eidolon-core` -> HTTP 400
- aktive `ephemeral_only`-Rolle -> HTTP 400
- `/projects` -> leer nach Dogfood-Cleanup
- `/backups` -> leer nach Testkontamination-Cleanup

Mobile-Dogfood:
- alle 11 Tabs sichtbar auf 390px-Viewport
- Healing-Button liegt im Viewport und ist klickbar
- Button löst echten Check aus und aktualisiert sichtbaren Check-State

---

## Evidence
- `dogfood-output/final-open-blocks/03-mobile-healing-click-fixed.png`

---

## Abschluss
- **Verifiziert am:** 2026-08-26
- **Rest-Risiko:** `low`
- **Follow-up nötig:** Kein bekannter akuter Fake-/Placebo-/Placeholder-Block mehr offen. Neue Features/Flows weiter mit denselben Verträgen prüfen.
