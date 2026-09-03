# Adaptive Workspace Foundation — Zusammenfassung

## Produktentscheidung
Eidolon erzeugt **keine hardcodierten Hubs**, sondern generiert **need-driven workspaces** aus:
1. Nutzerpräferenzen
2. wiederkehrenden Themen
3. aktuellem Unterstützungsbedarf
4. harten Sicherheitsgrenzen der UI

## Sicherheitsprinzip
Adaptive Arbeitsbereiche dürfen ausschließlich im Slot `adaptive-workspace-host` rendern.
Core-Navigation, Chat, Dashboard, Mesh, Status und Einstellungen bleiben gesperrt.

## Implementierte Foundation
- User Model Store
- Topic Attention Store
- Workspace Generator
- Workspace Registry
- Runtime-APIs
- UI Host + Fallback
- Regressionen

## Nächste sinnvolle Schritte
1. semantische Topic-/Entity-Erkennung
2. Proactive Assistance Engine
3. echte Workspace-Datenmodelle pro aktivem Bereich
4. adaptive Modulbibliothek mit Actions/Trackern/Decision-Flows
5. feinere Nutzersteuerung für automatische Vorschläge

## Phase 10B ergänzt
- semantische Themenlabels
- Proactive Assistance
- persistente Workspace-State-Daten
- UI für proaktive Hilfe

## Phase 10C ergänzt
- ausführende generische Workspace-Module
- persistentes module_data je Workspace
- Modulaktions-API
- UI-Aktionen für Tracker, Decision, Planning, Reflection

## Phase 10D ergänzt
- Workspace-Orchestrator
- next-best-action-Ausführung
- priorisierte Modusränge
- autonome Empfehlung pro Workspace

## Grenzaufhebung A ergänzt
- lernende Workspace-Orchestrierung mit Feedback
- QUIC-Transport-Stub durch reale Klassen ersetzt
- negatives Feedback senkt Empfehlungen nun wirklich

- echter QUIC-End-to-End-Test mit Nachrichtenaustausch als Regression verankert

- Pairing-QR wird jetzt serverseitig als echtes PNG-Data-URL geliefert; UI ist nicht mehr auf clientseitige QR-CDN-Renderung angewiesen

- Pairing-End-to-End erzeugt jetzt realen Peer-Zustand: akzeptierte Peers tauchen in Discovery und Inbox als pairing_accept auf

- QR-Scan öffnet jetzt echte Pairing-URL `/pairing/connect` statt Google-Suche; mobiles Auto-Pairing vorhanden

- Pairing-Zielseite nutzt jetzt manuellen Button-Flow mit Timeout und Retry statt sofortigem Auto-Disable
- persistenter Peer-State-Store (`peers.db`) ergänzt; Discovery merged jetzt Inbox-Ereignisse mit `reachable`/`last_seen`/`paired_at`
- Re-Pairing desselben Peers erzeugt kein Discovery-Duplikat mehr; Zustand/Namen werden aktualisiert
- Post-Pairing-Mesh-Nachrichten halten Peers im Zustand `reachable` und sind live/regressionsseitig verifiziert
- dedizierte Peer-Lifecycle-Endpunkte ergänzt (`/mesh/peers`, `/mesh/peers/{peer_id}`, `mark-offline`)
- Peer-Lebenszyklus ist jetzt im Produktpfad sichtbar: `reachable`, `stale`, `offline`
- Reconnect-/Rejoin-Logik ergänzt: `offline` Peers werden durch Mesh-Send oder Re-Pairing wieder `reachable`
- Re-Pairing aktualisiert Peer-Namen/Zustand weiter konsistent ohne Discovery-Duplikate
- Peer-Lifecycle-Werkzeuge komplettiert: `heartbeat`, `refresh`, `prune`
- Offline-Peers können jetzt via Heartbeat, Mesh-Send oder Re-Pairing sauber wieder `reachable` werden
- Block C: mobile Pairing-Seite zeigt Host-Adresse, Gerätekontext und Statusschritte statt nur eines nackten Buttons
- Host-UI aktualisiert sichtbare Geräte nach QR-Erzeugung automatisch über `/mesh/peers`-Polling
- Block D: `project_workspace` wurde von generischen Karten auf echten Projektkern mit Board/Graph/Details gehoben
- Die Workspace-Orchestrierung reagiert im Projektmodus jetzt live auf sichtbare Blocker (`recommended_mode board`, `Blocker auflösen`)
- Block D: Projektkarten sind jetzt direkt bearbeitbar (umbenennen, selektieren, löschen)
- Das Detailpanel folgt jetzt einem konkreten Projektobjekt statt nur generischem Fokus-Text
- Block D: Projektobjekte tragen jetzt strukturierte Betriebsfelder statt nur Label/Status
- Blockerfluss ist live konsistent: Karte und Detailpanel zeigen denselben Owner-/Blocker-/Notiz-Zustand
- Block D: Projekt-Workspaces werden jetzt auf einen vollständigen Kern mit Dependency-Schicht hochgezogen
- Blocker-Cockpit und Dependency-Lösen sind live im Workspace verifiziert
- Block D: Orchestrierung führt jetzt auf ausführbare Karten statt nur auf generische Board-Aktionen
- Die UI zeigt die konkrete Empfehlungs-Payload der Next-Best-Action sichtbar an
- Block D: Die Projektoberfläche wird jetzt als zusammenhängende Führungsfläche statt nur als Modulliste gerendert
- Der Ladepfad backfilled abgeleitete Projektzustände jetzt schon vor der ersten Mutation
- Block D: Das aktive Projektobjekt ist jetzt direkt aus der Oberfläche steuerbar
- Die Projektführung ist damit nicht mehr nur Statusanzeige, sondern echte Arbeitssteuerung
- Block D Core ist jetzt abgeschlossen
- Der Projektkern ist live vollständig: Board, Graph, Dependencies, Details, Next-Best-Action und Direktsteuerung
- Block E gestartet: Proaktive Hilfe hat jetzt Modus-, Dringlichkeits- und Cooldown-Logik
- UI und API unterstützen jetzt differenziertes Feedback auf Vorschläge
- Block E Relevanz-Ausbau: aktive Projektbereiche bekommen Assistenzvorrang über `priority_score`
- Vorschläge sind jetzt weniger generisch und enthalten Themen-Signale plus Workspace-Kontext
- Block E abgeschlossen: Proaktive Hilfe hat jetzt Anti-Spam-Visibility-Policy mit Suppressionsgründen
- Assistenzvorschläge werden jetzt sichtbar begrenzt und aktive Arbeitskontexte priorisiert
- Block F gestartet: Autonomie sieht jetzt den real aktiven Projekt-Workspace statt nur Health/Tasks
- `/autonomy/status` und `/autonomy/cycle` sind jetzt an Workspace-Kontext gekoppelt
- Block F: Workspace-gekoppelte Autonomie führt jetzt reale Projekt-Followups aus
- Autonomie kann live Blocker lösen und bereite Arbeit starten
- Block F: Workspace-Followups lernen jetzt persistent je Workspace-Typ
- Gelerntes Vertrauen aus Workspace-Autonomie fließt in die nächste Entscheidung zurück
- Block G: Rust-CLI ist jetzt im Workspace und startet den Python-Runtime-Pfad real
- Block G: Port-Wahrheit und echter Python/Bash-Skill-Executor im Hybridpfad verifiziert
- Block G: Rust-CLI chat/devices/diagnose laufen jetzt gegen echte Runtime-Endpunkte
- Block G: Live verifiziert über Rust-CLI auf Port 8016
- Block H: Overlay produktisiert und an echten Runtime-Port bindbar gemacht
- Block H: finaler Produktaudit live abgeschlossen
