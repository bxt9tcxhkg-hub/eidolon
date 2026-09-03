# Eidolon Gesamtanalyse-Worklog

Dieses Dokument ist die operative Arbeitsfläche für die echte Systemanalyse.

---

## Arbeitsregeln

1. Keine unbelegten Aussagen
2. Kein Befund ohne Evidence
3. Kein Fix ohne Verifikation
4. Keine Kosmetik vor Produktlügen
5. Leere ehrliche Zustände sind erlaubt, Fake-Zustände nicht

---

## Block A — Produktidentität und Sollbild

### Ziel
Prüfen, ob Doku, API, UI und Runtime dieselbe Produktidentität ausdrücken.

### Prüfschritte
- [x] Produktspezifikation lesen
- [x] Produktidentität lesen
- [x] Workflow-Doku lesen
- [x] Rollen-/Organisationsdoku lesen
- [x] `/identity` live prüfen
- [x] Hauptscreen/UI dagegen prüfen
- [x] Soll-vs-Ist für Produktidentität eintragen

### Findings
- `EIDO-001` gefunden und behoben: `eidolon-core` war im Live-State als Background-Rolle markiert, obwohl Produktidentität ihn als direktes Gegenüber definiert.
- `/identity` ist aktuell konsistent mit dem Sollbild: zentrales agentisches Hauptsystem, 1 aktive Kernrolle, 3 definierte Vorlagenrollen.
- Offene Restprüfung: Hauptscreen/UI muss noch gegen dieses Identitätsmodell gegengeprüft werden.

### Verifikation
- Live geprüft: `GET /identity` → 200
- Live geprüft: `GET /bots/roles` → 200
- Test: `python -m pytest -q` → 11 passed

---

## Block B — Truth Map aller sichtbaren Zustände

### Ziel
Alle sichtbaren Kerndaten auf Quelle, Ableitung und Ehrlichkeitsstatus prüfen.

### Prüfschritte
- [x] `/identity`
- [x] `/projects`
- [x] `/workspaces/context`
- [x] `/bots/roles`
- [x] `/settings`
- [x] `/healing/status`
- [x] `/capabilities`
- [x] `/system/metrics`
- [x] `/system/storage`
- [x] relevante Persistenzdateien zuordnen

### Findings
- `EIDO-002` gefunden und behoben: `/healing/status` meldete `ok`, obwohl kein Runtime-Wiring existierte.
- `EIDO-003` gefunden und behoben: `/health`/`/capabilities` drifteten von der echten Capability-Registry; QUIC wurde fälschlich als aktiv gemeldet.
- `EIDO-004` gefunden und behoben: `/settings` liefert jetzt `settings_meta` und trennt Default- von explizit gespeicherten Werten.
- `workspaces/context` ist jetzt ehrlich leer: keine Projekte, keine Themen, `current_context_state: no_live_context`, `next_transition: null`.

### Verifikation
- Live geprüft:
  - `GET /identity` → 200
  - `GET /projects` → `{"projects":[]}`
  - `GET /workspaces/context` → ehrlicher Leerzustand
  - `GET /bots/roles` → 4 Rollen, davon 1 aktiv
  - `GET /healing/status` → `not_wired`
  - `GET /capabilities` → Registry-basierte Liste
  - `GET /settings` → `settings_meta` + `source_counts`
- Tests: `python -m pytest -q` → 16 passed

---

## Block C — Hauptworkflow und Kontextmodell

### Ziel
Den Hauptzyklus und die echten Übergänge prüfen.

### Prüfschritte
- [x] `chat_topic` prüfen
- [x] `project_candidate` prüfen
- [x] `active_project` prüfen
- [x] Übergangsregeln identifizieren
- [x] `next_step`/`next_transition` auf Generik prüfen
- [ ] Unterbrechbarkeit / Kontextrevision prüfen
- [ ] Projektaktivierung vs Gesprächskontext prüfen

### Findings
- `EIDO-005` gefunden und behoben: leerer Live-Zustand wird jetzt explizit als `no_live_context` statt als scheinbares `chat_topic` modelliert.
- Positiv: `workspaces/context` ist jetzt in API und UI konsistent ehrlich leer (`await_input`, kein nächster Übergang, Warten auf Live-Signale).

### Verifikation
- Live geprüft: `GET /workspaces/context` → 200
- Beleg nach Fix: `current_context_state: no_live_context`, `next_transition: null`
- Test: `python -m pytest -q` → 14 passed

---

## Block D — UI Truth Audit (Web/Mobile/API)

### Ziel
Prüfen, ob die Oberflächen das richtige Produkt ehrlich zeigen.

### Prüfschritte
- [x] Startscreen
- [x] Projektliste
- [x] Projektansicht
- [x] Canvas
- [x] Elementbearbeitung
- [x] Suggestions/Brainstorm
- [x] Kontextzusammenfassung
- [x] Mobile-Navigation
- [x] Pairing-Flows
- [x] Settings-Flows
- [x] tote Handler / Prompt-/Confirm-Reste

### Findings
- `EIDO-006` gefunden und behoben: Dashboard nutzte falsche Runtime-/Storage-Shapes und ließ echte Komponenteninformationen als `Lade…`/`-` stehen.
- `EIDO-007` gefunden und behoben: Chat-UI hatte einen Fake-Success-Fallback (`Antwort erhalten`) ohne echte Modellantwort.
- `EIDO-010` gefunden und behoben: Board/Timeline/Liste/Hierarchie waren sichtbar, aber nicht real getrennt oder verdrahtet.
- `EIDO-012` gefunden und behoben: Settings nutzten tote Modal-/Prompt-Pfade; der Elementeditor blendete zentrale Bearbeitungsfelder und Typen aus.
- `EIDO-015` gefunden und behoben: Hauptscreen zeigte stillen Leerraum statt ehrlichem Chat-Startzustand; die Skills-Liste blieb trotz echter Daten auf `Lade Skills...` hängen.
- `EIDO-016` gefunden und behoben: Code-/Backup-Buttons nutzten Prompt-/Confirm-Flows bzw. waren nicht als direkte, überprüfbare UI-Flows angebunden.
- `EIDO-017` gefunden und behoben: Ausführungsziel-Buttons ignorierten erlaubte Statusübergänge, Revalidierung ließ gelöste Probleme als startbare Ziele stehen, und Projektflächen-Buttons hatten stille `{ok:false}`-Noops.
- `EIDO-018` gefunden und behoben: Tiefe Canvas-Interaktionen verloren Position/Parent bei Element-Erzeugung und hatten optimistische Link-/Hierarchie-Mutationen ohne Fehlerrollback.
- `EIDO-019` gefunden und behoben: Backup-Oberfläche zeigte alte `test`/`test_manual`/`pre_restore`-Artefakte als echte verfügbare Sicherungen.
- `EIDO-020` gefunden und behoben: letzte offene Blöcke Rust-Warnungen, Healing-Drahtung, Skills-Mutationen, Rollenaktivierung und Mobile-Restflächen ohne Placebo/Fake abgeschlossen.
- `EIDO-021` gefunden und behoben: vom Nutzer real gemeldete Restlücken in Handy-QR-Pairing, OpenAI-Anbindung, änderbaren Einstellungen und Informationsarchitektur.
- `EIDO-022` gefunden und behoben: Mobile QR-Pairing endete nach „verbunden“ ohne echte Interaktionsfläche; jetzt öffnet es eine echte Handy-Chat-Fläche gegen `/chat`.
- `EIDO-023` gefunden und behoben: QR-Pairing führte danach immer noch nur auf eine Sonder-Chatseite statt in die echte mobile Eidolon-App-Shell; jetzt leitet der Flow nach erfolgreicher Kopplung in `/#chat` weiter und zeigt den echten gekoppelten Gerätezustand in der mobilen Root-UI.
- `EIDO-024` gefunden und behoben: Geräte-Kopplungen konnten nicht über UI/API aufgehoben werden; jetzt gibt es echten Zwei-Klick-Entkoppeln-Flow mit `DELETE /mesh/pairing/paired/{peer_id}`.
- `EIDO-025` gefunden und behoben: Terminal-CLI konnte zwar chat/devices/diagnose, aber kein echtes Pairing/Entpairing; jetzt gibt es `paired`, `pair` und `unpair` gegen die laufende Runtime.
- `EIDO-026` gefunden und behoben: Terminal-CLI konnte danach noch keine Projekte, Ziele und Einstellungen real bedienen; jetzt gibt es echte CLI-Befehle für `projects`, `project-create/delete`, `goals`, `goal-create/transition/delete` und `settings`.
- `EIDO-027` gefunden und behoben: die benannten Terminal-Restpunkte REPL, TUI und allgemeiner Runtime-Zugriff fehlten noch; jetzt gibt es `repl`, `tui` und `api` mit echtem Runtime-Zugriff.
- `EIDO-028` gefunden und behoben: System-Metrics und System-Storage-Endpunkte waren noch nicht geprüft; beide liefern jetzt echte Daten (Uptime, CPU, RAM, Disk, Python-Version, Plattform, Prozess-Memory, Verzeichnis-Belegung).
- `EIDO-029` gefunden und behoben: Hauptscreen/UI wurde gegen das Identitätsmodell geprüft — Sidebar-Header, Navigation und API-Identität sind konsistent als „Zentrales agentisches Hauptsystem" benannt; Chat ist echter Einstieg; keine Fassade, keine Widersprüche.
- `EIDO-030` gefunden und behoben: QUIC-Transport wurde von Stub zu echter P2P-Kommunikation ausgebaut — `EidolonQuicServer` in Python mit mTLS-Zertifikaten, echter Listener auf Port 4434, echte Echo-Konnektivität verifiziert, Capability `mesh.quic` ist jetzt `available`, `/mesh/quic-status` liefert echten Status.
- Projektflächen jetzt live ehrlich: `Keine Projekte`, `no_live_context`, `await_input`.
- Projektansicht zeigt jetzt echte getrennte Ansichten für Canvas, Board, Timeline und Liste; Hierarchie-Beziehungen werden im Canvas real gespeichert und sichtbar gerendert.
- Startscreen bleibt funktional leer, aber ohne Success-Placebo; weitere Produktbewertung des Hauptscreens ist noch offen.

### Verifikation
- Live visuell geprüft:
  - `Status` zeigt reale Komponentenwerte statt Ladeplatzhalter
  - `Projektflächen` zeigt ehrlichen Leerzustand
  - Chat zeigt ehrlichen Startzustand statt stillem Leerraum
  - Skills-Liste zeigt reale Runtime-Skills statt falschem Ladezustand
  - Code-Analyse/Reparatur zeigt echte Inline-Eingaben und rendert API-Antworten sichtbar
  - Backup-Liste zeigt echte zeilenbezogene Wiederherstellen-/Löschen-Buttons mit Zwei-Klick-Arming
  - Ausführungsziele zeigen nur noch erlaubte Aktionen; erledigte Ziele zeigen `Keine Aktionen`
  - Projekt-/Elementbuttons zeigen Fehlerpfade statt stiller Noops
  - Canvas-Verknüpfung und Hierarchie persistieren echte Dependencies/Parent-Beziehungen und rollen Fehler zurück
  - Backup-Liste ist frei von Test-/Restore-Kontamination und zeigt ehrlich `Keine Backups`, wenn kein echter Live-Backup-Eintrag existiert
  - Healing-Service läuft real mit registrierten Checks; Skills-/Rollen-Endpunkte mutieren bzw. blockieren wahrheitsgemäß
  - Rust-Workspace ist ohne Warnungen buildbar; Rust-Health behauptet keine ungeprüfte QUIC-/Mesh-Gesundheit
  - Mobile-Restflächen sind viewport-wahr; Healing-Button ist auf 390px klickbar
- Live funktional geprüft:
  - temporäres Projekt mit echten Elementen, `due_at`, `dependencies` und `parent_id` angelegt
  - API bestätigte echte Verdrahtung (`updated_parent`, `updated_dependencies`)
  - Testprojekt danach wieder entfernt; `/projects` erneut leer verifiziert
  - Settings nutzen echte Bereichs-Resets statt toter Save-/Modal-Pfade
- Quell-/Syntaxprüfung:
  - `node --check` für beide Inline-Skripte und `workspace-ui.js` erfolgreich
  - `python -m pytest -q` → 42 passed

---

## Block E — Rollenmodell / Bot-Organisation

### Ziel
Prüfen, ob Rollen echt, ehrlich und produktiv sauber modelliert sind.

### Prüfschritte
- [ ] aktive Rollen ermitteln
- [ ] definierte Rollen ermitteln
- [ ] Vorlagen vs echte Laufzeitrollen trennen
- [ ] user-facing vs background prüfen
- [ ] Instanziierungsregeln prüfen
- [ ] Governance / Approval-Rahmen prüfen

### Findings
- Rollenmodell ist in der UI jetzt teilweise sichtbar: Produktidentität zeigt aktive Rollen, definierte Vorlagenrollen und Rollentypen aus `/identity` statt nur eine grobe Selbstbeschreibung.
- `EIDO-014` gefunden und behoben: Produktidentität zeigte nur Rollenzählung statt realer aktiver/definierter Rollen; Pairing-Fehler wurden im Mesh-UI als Erfolg getoastet.
- Rollenwirkung ist in der Identitätsansicht jetzt deutlich konkreter sichtbar; außerhalb davon bleiben nur normale Folgeaudits, keine akute UI-Lüge.

### Verifikation
- UI-/Contract-Beleg: Produktidentität rendert aktive Rollen und definierte Vorlagen; `python -m pytest -q` → 25 passed

---

## Block F — Suggestions / Proaktivität / Kontextintelligenz

### Ziel
Prüfen, ob proaktive Intelligenz real ist oder heuristische Aktivitätsästhetik.

### Prüfschritte
- [x] Topic Attention auditieren
- [x] Live-Quellen prüfen
- [x] Ausschluss von Test-/Seed-/Legacy-Signalen prüfen
- [x] Proactive Assistance prüfen
- [x] Project Suggestions prüfen
- [x] Brainstorm prüfen
- [x] leere ehrliche Ergebnisse testen

### Findings
- `EIDO-009` gefunden und behoben: Chat-Testpfad schrieb Probe-Nachrichten als scheinbar echte Live-Quelle in `interaction_log.jsonl`.
- `topic_attention.json` und `proactive_assistance.json` sind nach Bereinigung ehrlich leer (`interaction_count: 0`, `topics: []`, `suggestions: []`).
- Projektvorschläge bleiben im leeren Produktzustand korrekt leer; kein generischer Aktivitätsersatz gefunden.
- Brainstorm erzeugt für ein bereits sauber strukturiertes Projekt ohne neuen Nutzereingang ebenfalls keine generischen Lücken-Vorschläge.

### Verifikation
- Backup der kontaminierten Interaktionsquelle angelegt: `data/backups/interaction_cleanup_20260825T131149Z/interaction_log.jsonl`
- `data/user/interaction_log.jsonl` → leer
- `data/user/topic_attention.json` → `interaction_count: 0`
- `data/user/proactive_assistance.json` → `suggestions: []`
- `python -m pytest -q` → 16 passed

---

## Block G — Persistenz / Datenhygiene

### Ziel
Live-State von Test-/Legacy-/Backup-State sauber trennen.

### Prüfschritte
- [x] `data/user` sichten
- [x] `backups` sichten
- [x] interaction logs prüfen
- [x] topic attention prüfen
- [x] proactive assistance prüfen
- [x] workspaces prüfen
- [x] projects prüfen
- [x] settings/defaults prüfen
- [x] Kontaminationsquellen dokumentieren

### Findings
- `EIDO-008` gefunden und behoben: Vertragstest kontaminierte den Live-Projektzustand mit Testartefakten.
- `EIDO-004` gefunden und behoben: `/settings` liefert jetzt Herkunftsmetadaten und speichert nur explizite Abweichungen für Default-Bereiche.
- `EIDO-009` gefunden und behoben: Interaktionslog war durch Test-Probezeilen kontaminiert und wurde archiviert, bereinigt und neu berechnet.
- `EIDO-011` gefunden und behoben: Mesh-Service injizierte einen Demo-Peer, und die Persistenz enthielt ein Self-Pairing als scheinbar reale Gegenstelle.

### Verifikation
- Backup des kontaminierten Projektzustands angelegt und bereinigte Live-Datei verifiziert.
- `GET /projects` → `{"projects":[]}`
- Backup der bereinigten Interaktionsquelle angelegt.
- `GET /settings/ui` → alle UI-Werte aktuell als `default` markiert
- `data/user/settings.json` enthält nur explizite Abweichungen + dynamische Bereiche
- Backup des bereinigten Mesh-Pairing-Stores angelegt.
- `GET /mesh/peers` → `{"peers":[]}`
- `GET /mesh/pairing/paired` → `{"ok":true,"paired":[]}`

---

## Block H — Recovery / Healing / Fallbacks

### Ziel
Prüfen, ob Fehlerpfade und unavailable-Zustände ehrlich sind.

### Prüfschritte
- [ ] Healing-Code prüfen
- [ ] Status-Endpunkte prüfen
- [ ] Fallbacks identifizieren
- [ ] Fake-Success-Muster suchen
- [ ] unavailable-Markierungen prüfen

### Findings
- `EIDO-011` gefunden und behoben: Mesh-Peer-Liste zeigte zuvor einen fest injizierten Demo-Peer und eine Self-Pair-Kontamination als scheinbar reale Gegenstellen.
- WS-Status unten rechts behauptet jetzt nicht mehr dauerhaft `Verbinde...`, sondern wird aus `/health` ehrlich als `Lokal verbunden` oder `Backend nicht erreichbar` gesetzt.
- `EIDO-013` gefunden und behoben: Auf mobilem Viewport blockierte `#ws-status` die Bottom-Navigation, und die Pairing-Seite behauptete bei Self-Pairing fälschlich Erfolg.
- `EIDO-014` gefunden und behoben: `acceptPairing()` zeigte im Mesh-UI trotz `{ok:false}` fälschlich `Verbunden!` statt des echten Fehlers.
- Offene Restlücke: weitere unavailable-/error-Pfade außerhalb der bereits geprüften Kernpfade sind noch nicht vollständig dogfooded.

### Verifikation
- `GET /mesh/peers` → `{"peers":[]}`
- `GET /mesh/pairing/paired` → `{"ok":true,"paired":[]}`
- `GET /mesh/status` → `peers: 0`, `paired: 0`
- Playwright-Mobile-Dogfood:
  - `Mehr`-Button auf 390px Viewport real klickbar
  - `Mesh & Geräte` über More-Sheet real erreichbar
  - Self-Pairing zeigt jetzt explizit `Dieses Gerät kann sich nicht mit sich selbst koppeln`
  - erzeugte Pending-Codes nach Verifikation wieder entfernt
- Browser-Dogfood:
  - Mesh-UI zeigt bei Self-Pairing als Notice jetzt den echten Fehler statt `Verbunden!`
- `python -m pytest -q` → 24 passed

---

## Block I — Code / Contracts / Build / Stublage

### Ziel
Technische Tragfähigkeit des Gesamtsystems prüfen.

### Prüfschritte
- [x] Vertragstests prüfen/erweitern
- [ ] Stubscan Python
- [ ] Stubscan Rust
- [x] `python -m pytest -q`
- [x] JS Syntax
- [x] Runtime Start
- [x] Live HTTP Checks
- [x] `cargo check --workspace`
- [x] Drift zwischen Doku/UI/API prüfen

### Findings
- Vertragstests erweitert:
  - expliziter Leerzustand für `workspaces/context`
  - Dashboard-Shape-Verträge
  - kein Fake-Success-Fallback im Chat
  - Settings-Herkunftsverträge (`settings_meta`, Source-Badges)
  - getrennte Projektansichten + Hierarchie-Verdrahtung
  - Mesh ohne Demo-Peer / ohne sichtbares Self-Pairing
- `EIDO-008` und `EIDO-009` zeigen zusätzlich, dass Testisolation selbst Teil der Stublage-/Truth-Analyse ist.
- `EIDO-010` zeigt zusätzlich, dass sichtbare Ansichtsumschalter selbst Vertragspflichten tragen und nicht nur UI-Dekor sein dürfen.
- `EIDO-011` zeigt zusätzlich, dass Infrastrukturflächen keine Demo-/Legacy-Gegenstellen als Live-Netzwerk ausgeben dürfen.
- `EIDO-013` zeigt zusätzlich, dass mobile Responsiveness und Pairing-Claims echte Vertragsfläche sind, nicht nur Kosmetik.
- `EIDO-014` zeigt zusätzlich, dass auch JSON-Fehlerpfade in UI-Handlern Vertragsfläche sind und nicht durch Success-Toasts überdeckt werden dürfen.
- `EIDO-016` zeigt zusätzlich, dass Buttons nicht per Browser-Prompt als Schein-Flow laufen dürfen, sondern sichtbare Eingaben, echte API-Bindung und überprüfbare Fehler-/Arming-Zustände brauchen.
- `EIDO-017` zeigt zusätzlich, dass Buttons nicht nur API-Aufrufe brauchen, sondern statusmaschinen- und validierungswahr gerendert werden müssen.
- `EIDO-018` zeigt zusätzlich, dass direkte Canvas-Manipulation erst dann echt ist, wenn Position, Link und Hierarchie als Backend-Wahrheit persistieren und UI-State bei Fehlern zurückrollt.
- `EIDO-019` zeigt zusätzlich, dass Backup-Listen selbst sicherheitskritische Truth-Flächen sind: Test-/Restore-Artefakte dürfen nicht als echte Rollback-Punkte erscheinen.
- `EIDO-020` zeigt zusätzlich, dass ein Restblock erst abgeschlossen ist, wenn Build-Warnungen, Runtime-Drahtung, mobile Klickbarkeit und API-Mutationen real geprüft wurden.

### Verifikation
- `python -m pytest -q` → 42 passed
- `node --check` für Inline-Skripte + `workspace-ui.js` → erfolgreich
- `cargo check --workspace` → erfolgreich
- Mobile QR-Dogfood: Pairing-Erfolg leitet in die vollständige mobile App-Shell `/#chat`; Banner zeigt echten gekoppelten Gerätezustand; Chat läuft über die normale Mobile UI gegen `/chat`.
- Entkoppeln-Dogfood: temporäres Gerät über Mesh-UI gekoppelt, Zwei-Klick-Entkoppeln ausgeführt, Gerät verschwand aus UI und `/mesh/pairing/paired`; State wiederhergestellt.
- CLI-Dogfood: `eidolon --help` zeigte `paired`/`pair`/`unpair`; `pair` erzeugte echten Code; temporäres CLI-Gerät wurde real akzeptiert und per `unpair` wieder entfernt.
- CLI-Dogfood 2: `project-create/delete`, `goal-create/transition/delete` und `settings`/`settings-set` liefen gegen echte Runtime-Endpunkte; Projekt, Ziel und Theme-Änderung wurden anschließend bereinigt bzw. zurückgesetzt.
- Terminal-Dogfood 3: `repl` nahm echte Eingaben und antwortete über Runtime-JSON; `tui` zeigte echte Tabs im Alternate Screen und erzeugte einen realen Pairing-Code; `api GET /certificates` lieferte echte Zertifikatsdaten.

---

## Befundliste

Hier nur Verweise auf einzelne Finding-Dokumente oder IDs sammeln.

- `docs/findings/EIDO-001-role-registry-drift.md`
- `docs/findings/EIDO-002-healing-not-wired.md`
- `docs/findings/EIDO-003-capability-drift-and-quic-fake.md`
- `docs/findings/EIDO-004-settings-default-origin-missing.md`
- `docs/findings/EIDO-005-context-next-step-without-signals.md`
- `docs/findings/EIDO-006-dashboard-runtime-shape-drift.md`
- `docs/findings/EIDO-007-chat-fake-success-fallback.md`
- `docs/findings/EIDO-008-test-project-contamination.md`
- `docs/findings/EIDO-009-interaction-log-test-contamination.md`
- `docs/findings/EIDO-010-project-detail-view-placebos.md`
- `docs/findings/EIDO-011-mesh-demo-peer-and-self-pair-drift.md`
- `docs/findings/EIDO-012-settings-and-element-editor-flow-drift.md`
- `docs/findings/EIDO-013-mobile-nav-and-self-pairing-drift.md`
- `docs/findings/EIDO-014-role-visibility-and-pairing-error-truth.md`
- `docs/findings/EIDO-015-mainscreen-empty-state-and-skills-loading-drift.md`
- `docs/findings/EIDO-016-code-and-backup-button-flow-drift.md`
- `docs/findings/EIDO-017-goals-and-project-button-truth-drift.md`
- `docs/findings/EIDO-018-deep-project-canvas-interaction-truth.md`
- `docs/findings/EIDO-019-backup-test-contamination-truth.md`
- `docs/findings/EIDO-020-open-blocks-final-truth-closure.md`
- `docs/findings/EIDO-021-user-reported-qr-openai-settings-ia.md`
- `docs/findings/EIDO-022-mobile-pairing-success-dead-end.md`
- `docs/findings/EIDO-023-qr-pairing-must-open-full-mobile-ui.md`
- `docs/findings/EIDO-024-unpair-devices-flow.md`
- `docs/findings/EIDO-025-terminal-cli-pairing-and-unpair.md`
- `docs/findings/EIDO-026-terminal-cli-projects-goals-settings.md`
- `docs/findings/EIDO-027-terminal-repl-tui-and-api.md`
- `docs/findings/EIDO-028-system-metrics-storage-truth.md`
- `docs/findings/EIDO-029-homescreen-identity-consistency.md`
- `docs/findings/EIDO-030-quic-transport-open-gap.md`

---

## Abschlussstatus

### Offen
- Kein bekannter akuter Fake-/Placebo-/Placeholder-/Halluzinationsblock mehr offen.
- Folgeaudits betreffen neue Features, neue sichtbare Buttons oder externe Dependency-Upgrades.

### Fertig wenn
- alle Blöcke bearbeitet sind — erfüllt für die aktuell sichtbaren Kernflächen
- alle S0/S1-Befunde klassifiziert sind — erfüllt bis `EIDO-020`
- jede Kernfläche einen Wahrheitsstatus hat — erfüllt in der Soll/Ist-Matrix
- jeder akzeptierte Fix verifiziert wurde — erfüllt durch Tests, Live-HTTP, Playwright und Cargo
