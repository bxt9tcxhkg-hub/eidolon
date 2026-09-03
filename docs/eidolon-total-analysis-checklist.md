# Eidolon Gesamtanalyse-Checkliste

Ziel: Fehlende Parts, Placebos, Fakes, Halluzinationen, Fehler und halbfertige Architektur systematisch finden, priorisieren, beheben und Eidolon als Gesamtsystem belastbar fertig bekommen.

---

## 0. Arbeitsregel: Was diese Analyse nicht sein darf

Die Analyse ist **nicht**:
- ein reines Code-Review
- ein UI-Schönheitscheck
- eine lose Bugliste
- eine Roadmap mit unbelegten Annahmen

Die Analyse ist:
- **evidence-first**
- **truth-first**
- **systemweit**
- **Soll-vs-Ist-basiert**
- **mit Live-Verifikation**

Jeder Befund braucht:
- klare Quelle
- klare Wirkung
- klare Klassifikation
- klare Done-Definition

---

## 1. Pflicht-Artefakte der Gesamtanalyse

Am Ende muss die Analyse diese 9 Artefakte liefern.

### A1. Produkt-Sollbild
- Ein-Satz-Definition: Was ist Eidolon?
- Gegenabgrenzung: Was ist Eidolon explizit nicht?
- Kernversprechen
- Hauptworkflow
- Rollenmodell
- Wahrheitspflichten des Produkts

### A2. Soll-vs-Ist-Matrix
Pro Kernfunktion:
- Sollbeschreibung
- reale Implementierung
- Beleg
- Status: `fehlt | halb | fake | echt | verifiziert`
- betroffene Dateien / Endpunkte / Oberflächen

### A3. Truth Map
Für jede sichtbare Information:
- UI/API-Feld
- Quellsystem
- Ableitungspfad
- Live/Default/Heuristik/Test/Legacy
- Ehrlichkeitsstatus

### A4. Workflow Map
- Zustände
- Übergänge
- Trigger
- Fehlerpfade
- Unterbrechungspunkte
- Verifikationspunkte

### A5. UI Truth Audit
- Web
- Mobile
- API
- ggf. Desktop / Runtime
- tote Elemente
- Attrappen
- direkte vs indirekte Interaktion

### A6. Runtime-/Architektur-Audit
- Rollen
- Persistenz
- Kontextmodell
- Recovery/Fallbacks
- Capability-Wahrheit

### A7. Code-/Build-/Contract-Audit
- Stubscan
- Contract Checks
- Tests
- Compile/Build
- Live-Endpunkte

### A8. Priorisierte Gap-Liste
Klassen:
- `P0 Fake/Placebo`
- `P1 fehlender Produktkern`
- `P2 Qualitätsmangel`
- `P3 Politur`

### A9. Fertigstellungsdefinition
- objektive Kriterien
- verifizierbare Endzustände
- was erfüllt sein muss, bevor Eidolon als „fertig“ gilt

---

## 2. Fundklassen

Jeder Befund muss genau einer Primärklasse zugeordnet werden.

### F1. Fake
Etwas wird als real, aktiv, intelligent oder verdrahtet dargestellt, ist es aber nicht.

Beispiele:
- Erfolgsmeldung ohne echte Ausführung
- Bot wirkt aktiv, ist aber nur Template
- Suggestion wirkt intelligent, kommt aber aus generischem Fallback

### F2. Placebo
Etwas liefert das Gefühl von Fortschritt, Kontext oder Intelligenz, ohne reale Substanz.

Beispiele:
- generische „nächste Schritte“ ohne echte Evidenz
- künstlicher Kontext aus irrelevanten/Testquellen
- Defaultwerte als gelernt inszeniert

### F3. Halluzination
Das System behauptet Zustand, Struktur oder Zusammenhang ohne belastbare Quelle.

Beispiele:
- Projektkandidat ohne tragende Signale
- erfundene Verantwortlichkeiten
- nicht existierende Zusammenhänge zwischen Elementen

### F4. Placeholder
Temporäre Struktur ohne echte Funktion.

Akzeptabel nur, wenn klar markiert als:
- Default
- leer
- nicht verdrahtet
- noch nicht verfügbar

### F5. Missing Part
Kritische Funktion oder Architekturstufe fehlt real.

### F6. Defect
Konkreter technischer Fehler.

Beispiele:
- toter Handler
- kaputter Endpunktvertrag
- Buildfehler
- Race Condition
- fehlerhafte Zustandslogik

### F7. Drift
Doku, UI, API und Code erzählen nicht mehr dieselbe Wahrheit.

---

## 3. Severity-Modell

### S0 — Produktlüge / Vertrauensbruch
- Fake
- Placebo
- Halluzination
- falscher Aktivzustand
- falsche Erfolgsdarstellung

### S1 — Kernblocker
- Hauptworkflow nicht durchführbar
- Kontextzustände inkonsistent
- zentrale Rollen-/Projektlogik fehlt

### S2 — erheblicher Qualitätsmangel
- UI schwer/indirekt
- wichtige Verträge unklar
- Warnungen / Inkonsistenzen / Nebenmodule schwach

### S3 — Politur / Finish
- unnötige Reibung
- Sichtbarkeitsprobleme
- schwache Text-/Visual-Hierarchie

---

## 4. Evidence-Schema für jeden Befund

Jeder Fund muss in exakt diesem Schema dokumentiert werden.

```yaml
id: EIDO-XXX
category: fake | placebo | hallucination | placeholder | missing_part | defect | drift
severity: S0 | S1 | S2 | S3
surface: web | mobile | api | runtime | storage | docs | rust | python
area: product_identity | workflow | roles | context | suggestions | projects | healing | mesh | ui | persistence
summary: Kurzbeschreibung des Problems
claim: Welche implizite/ explizite Behauptung das System aktuell macht
reality: Was tatsächlich der Fall ist
source_of_truth:
  - file / endpoint / runtime output
proof:
  - test output
  - live response
  - screenshot
  - code path
impact: Warum das kritisch ist
fix_required: Welche Änderung nötig ist
verification:
  - test
  - live endpoint check
  - build check
  - UI interaction check
done_when: Objektive Abschlussbedingung
```

---

## 5. Prüfkatalog — Block für Block

# Block A — Produktidentität und Sollbild

## Ziel
Prüfen, ob Eidolon als Produkt sauber definiert ist und ob System, UI, API und Runtime dieselbe Identität ausdrücken.

## Muss geprüft werden
- zentrale Spezifikationen
- Produktidentität
- Soll-Workflow
- Autonomie-Vertrag
- Rollen-/Organisationsmodell
- UI-Architektur
- Repo-Grenzen
- Implementierungsplan

## Fragen
- Ist in einem Satz klar, was Eidolon ist?
- Ist klar, was Eidolon nicht ist?
- Ist es ein Agent oder nur eine Tool-Oberfläche?
- Ist es ein zentrales Hauptsystem oder ein Set loser Features?
- Widersprechen sich Doku, API und UI?

## Funde suchen nach
- alter Produktidentität
- verschiedenen konkurrierenden Mental Models
- Resten alter Konzepte
- Dokumenten, die nie produktisiert wurden

## Done
- ein konsistentes Sollbild existiert
- alle Kernbegriffe sind operationalisiert
- Widersprüche dokumentiert oder beseitigt

---

# Block B — Truth Map aller sichtbaren Zustände

## Ziel
Jede sichtbare Information auf Wahrheitsstatus prüfen.

## Zu prüfen pro sichtbarem Feld
- Name
- UI/API-Ort
- Quelle
- Berechnung
- Aktualität
- Wahrheitstyp

## Wahrheitstypen
- `live`
- `derived_honest`
- `default_marked`
- `unavailable_explicit`
- `contaminated`
- `fake`

## Pflichtbereiche
- identity
- project lists
- workspace context
- bot roles
- suggestions
- goals
- healing
- capabilities
- metrics
- storage
- pairing

## Funde suchen nach
- Seed-/Test-/Legacy-Kontamination
- generischen Statuszeilen
- UI-Labels ohne belastbare Quelle
- stillen Defaults
- Heuristik als Wahrheit

## Done
- jede Kernanzeige ist einer realen Quelle zugeordnet
- Fake/contaminated Anzeigen entfernt oder ehrlich ummarkiert

---

# Block C — Hauptworkflow-Analyse

## Ziel
Den eigentlichen Produktkern prüfen.

## Soll-Zyklus
1. verstehen
2. strukturieren
3. einordnen
4. organisieren
5. ausführen
6. verifizieren
7. fortsetzen

## Pflichtprüfung je Stufe
- Input
- interner Zustand
- sichtbare UI
- API-Repräsentation
- erlaubte Übergänge
- Failure Modes
- Unterbrechbarkeit

## Kernzustände
- `chat_topic`
- `project_candidate`
- `active_project`

## Konkrete Fragen
- Wann wird aus Gespräch ein Kandidat?
- Wann wird aus Kandidat ein aktives Projekt?
- Wer ist verantwortlich?
- Wie wird `next_step` erzeugt?
- Gibt es echte Verifikation?
- Was passiert bei neuem Input mitten in der Ausführung?

## Funde suchen nach
- impliziten statt expliziten Übergängen
- leeren Übergängen
- generischen `next_step`
- fehlender Unterbrechungslogik
- Diskrepanz zwischen State und UI

## Done
- Zustände und Übergänge sind systemisch sichtbar
- keine Phase wird nur behauptet
- Kontext bleibt bei Interrupts konsistent

---

# Block D — UI Truth Audit

## Ziel
Prüfen, ob Web/Mobile/API wirklich das richtige Produkt zeigen.

## D1. Strukturprüfung
- Was sieht man zuerst?
- Ist der Fokus klar?
- Ist die UI agentisch oder verwaltungsartig?
- Werden Bedeutung und Zustand stärker gezeigt als Technik?

## D2. Interaktionsprüfung
- direkte Manipulation vorhanden?
- unnötige Modals / Prompts / Confirms?
- tote Buttons?
- native Notbehelfe?
- echte Mobile-Flows?

## D3. Zustandsprüfung
Sind diese Zustände sichtbar?
- draft
- proposal
- approved
- executing
- verified
- blocked
- unavailable
- empty but honest

## D4. Ehrlichkeitsprüfung
- zeigt die UI Leere ehrlich?
- zeigt sie fehlende Verdrahtung ehrlich?
- zeigt sie echte Aktivität statt bloß Aktivitätsästhetik?

## Pflichtbereiche
- Startscreen
- Projektliste
- Projektansicht
- Canvas
- Elementeditor
- Suggestions/Brainstorm
- Kontextansicht
- Pairing-Seiten
- Settings
- Mobile Nav

## Funde suchen nach
- CSS ohne echte Funktion
- Fake-Fokus
- manuelle Reibung statt agentischer Führung
- Visuals, die Aktivität vortäuschen

## Done
- keine tote Kerninteraktion
- keine falsche State-Darstellung
- direkte Interaktion in Kernpfaden
- ehrliche Empty-/Unavailable-States

---

# Block E — Rollen- und Agentenmodell

## Ziel
Prüfen, ob das Rollenmodell real ist und sauber zwischen aktiv, definiert und nicht vorhanden trennt.

## Muss geprüft werden
- welche Rollen existieren?
- welche sind aktiv?
- welche sind nur Templates?
- welche sind user-facing?
- welche sind background only?
- welche benötigen explizite Freigabe?

## Pflichtfelder pro Rolle
- purpose
- responsibilities
- non_responsibilities
- activation_triggers
- autonomy_level
- direct_user_counterpart
- requires_user_approval
- context_sources
- success_metrics
- role_kind
- instantiation_policy
- status

## Funde suchen nach
- aktive Rollen ohne echte Laufzeitfunktion
- Templates, die als laufende Bots wirken
- fehlende Governance bei autonomer Instanziierung
- Rollen ohne klare Nicht-Verantwortung

## Done
- Rollenstatus ist ehrlich
- aktive Rollen sind real aktiv
- definierte Rollen sind als definiert markiert
- keine stille Organisationsmacht

---

# Block F — Suggestions / Proaktivität / Kontextintelligenz

## Ziel
Prüfen, ob Eidolon wirklich hilfreiche Kontextintelligenz hat oder nur heuristische Scheinintelligenz.

## Muss geprüft werden
- Topic Attention
- Workspace Generation
- Proactive Assistance
- Project Suggestions
- Brainstorm
- Context Transitions

## Kernfragen
- Kommen Vorschläge aus realen Signalen?
- Gibt es Evidenz je Vorschlag?
- Werden irrelevante/Testquellen ausgeschlossen?
- Gibt es leere Ergebnisse, wenn keine realen Signale vorliegen?
- Wird generischer Fallback vermieden?

## Funde suchen nach
- generische Review-/Next-Step-Fallbacks
- Bigram-/Heuristikmüll als „Thema“
- proaktive Karten ohne echte Substanz
- Suggestions ohne Impact oder Evidenz

## Done
- Vorschläge sind evidenzbasiert oder leer
- keine Suggestions nur für Aktivitätsgefühl
- Live-Signale klar getrennt von Test/Seed

---

# Block G — Persistenz und Datenhygiene

## Ziel
Prüfen, ob Live-State, Default-State, Test-State, Backup-State und Legacy-State sauber getrennt sind.

## Muss geprüft werden
- data/user
- backups
- autonomy logs
- interaction logs
- topic attention
- proactive assistance
- bot roles
- workspaces
- projects
- settings

## Fragen
- Was ist Live-State?
- Was ist Cache?
- Was ist Archiv?
- Was ist Backup?
- Was darf in Produktsicht auftauchen?
- Was muss strikt verborgen/ignoriert bleiben?

## Funde suchen nach
- Testobjekte im Live-System
- Legacy-Projekte in echten Listen
- Verifikationsartefakte als Produktsignal
- Kontamination von Topic-/Project-Ableitung

## Done
- Datenklassen sauber getrennt
- keine Kontamination des Live-Produkts
- Bereinigung dokumentiert und reversibel

---

# Block H — Recovery / Healing / Fallback-Wahrheit

## Ziel
Prüfen, ob das System Fehler ehrlich meldet und Recovery nicht simuliert.

## Muss geprüft werden
- healing status
- recovery hooks
- refactor hooks
- failure paths
- unavailable capabilities

## Fragen
- Meldet das System Erfolg ohne reale Aktion?
- Gibt es Stub-Recovery?
- Gibt es unehrliche „ok“-States?
- Wird unavailable explizit gezeigt?

## Done
- kein Fake-Recovery
- unavailable sauber markiert
- jeder Erfolgsstatus hat reale Wirkung

---

# Block I — Code-/Contract-/Build-Audit

## Ziel
Sicherstellen, dass nicht nur Produktpfade ehrlich sind, sondern der Unterbau auch real tragfähig ist.

## I1. Contract Audit
Für Kernrouten prüfen:
- Request-Schema
- Response-Schema
- Fehlerfälle
- UI-Abhängigkeit
- Tests

## I2. Stub Audit
Suchen nach:
- leeren Dateien
- Modulexporte ohne Substanz
- Dummy-/Fake-/Stub-/Mock-Reste
- generische Fallbacks

## I3. Build Audit
Pflichtläufe:
- `python -m pytest -q`
- JS Syntax Check
- Runtime Start
- Live HTTP Checks
- `cargo check --workspace`

## I4. Drift Audit
- Doku ≠ Code
- UI ≠ API
- API ≠ Persistenz
- Runtime ≠ behauptete Fähigkeiten

## Done
- Kernmodule buildbar/testbar
- Stub-Schulden entweder beseitigt oder ehrlich isoliert
- Verträge stimmen zwischen UI/API/Runtime überein

---

## 6. Prüfkatalog für jede Kernfläche

Für jede relevante Fläche diese 12 Fragen beantworten:

1. Was behauptet diese Fläche?
2. Welche reale Quelle stützt das?
3. Ist der Zustand live oder abgeleitet?
4. Falls abgeleitet: ist die Ableitung nachvollziehbar?
5. Gibt es Test-/Legacy-/Seed-Kontamination?
6. Kann die Fläche leer ehrlich leer sein?
7. Gibt es generische Fallbacks?
8. Gibt es tote Interaktionen?
9. Gibt es sichtbare, aber nicht reale Fähigkeiten?
10. Was ist der Failure Mode?
11. Wie wird verifiziert, dass sie echt funktioniert?
12. Wann gilt die Fläche als fertig?

---

## 7. Minimaler Verifikationssatz pro Fix

Kein Fix zählt ohne Verifikation.

### Für jeden Fix Pflicht
- passende Tests oder neue Vertragstests
- Syntax/Compile-Check
- Live-HTTP-Check oder Runtime-Check
- falls UI betroffen: echter UI-Check
- wenn State betroffen: Persistenz-/Quelle prüfen

### Fix gilt erst als abgeschlossen wenn
- der Fake/Fehler verschwunden ist
- keine neue Produktlüge entstanden ist
- die Oberfläche ehrlich bleibt, auch im leeren Zustand
- die Änderung reproduzierbar belegbar ist

---

## 8. Priorisierungslogik

### Reihenfolge der Bearbeitung
1. **S0 Produktlügen**
2. **S1 Hauptworkflow-Lücken**
3. **S1 Rollen-/Kontextmodell-Lücken**
4. **S0/S1 Vorschlags-/Proaktivitätslügen**
5. **S1 Persistenz-/Kontaminationsprobleme**
6. **S2 Runtime-/Build-/Contract-Probleme**
7. **S2/S3 UI-Politur**

### Regel
Nie zuerst schöne UI bauen, wenn darunter noch Produktlügen liegen.

---

## 9. Definition „Eidolon ist als Ganzes fertig“

Eidolon gilt erst dann als fertig, wenn **alle** folgenden Bedingungen erfüllt sind:

### Produkt
- Produktidentität ist eindeutig
- keine konkurrierenden Mental Models mehr

### Wahrheit
- keine Kernfläche spielt Aktivität, Kontext oder Fähigkeit vor
- Defaults sind als Defaults erkennbar
- unavailable ist ehrlich als unavailable markiert
- Empty-State ist ehrlich leer

### Workflow
- Hauptzyklus ist real implementiert und sichtbar
- Übergänge zwischen `chat_topic`, `project_candidate`, `active_project` sind belastbar
- `next_step`/`next_transition` sind nicht generisch-fake

### UI
- keine toten Kerninteraktionen
- keine prompt/confirm-Notbehelfe in Kernflows
- direkte Manipulation in relevanten Arbeitsflächen
- keine Verwaltungsästhetik statt Agentik im Hauptfluss

### Rollenmodell
- aktive Rollen sind real aktiv
- definierte Rollen sind nicht als aktiv getarnt
- Instanziierungsregeln sind explizit

### Kontext / Proaktivität
- Vorschläge kommen aus realen Signalen oder bleiben leer
- kein Heuristikmüll als Produktintelligenz
- kein generischer Fortschrittsersatz

### Persistenz
- kein Test-/Seed-/Legacy-Schmutz im Live-Produkt
- Datenquellen sauber getrennt

### Technik
- Kernpfade getestet
- Runtime startet sauber
- Kernrouten live verifiziert
- Workspace/Rust/Python-Build real tragfähig

---

## 10. Empfohlenes Arbeitsformat für die eigentliche Gesamtanalyse

Für die Durchführung selbst in Blöcken arbeiten:

### Block 1
Produktidentität + Sollbild + Artefakt A1/A2

### Block 2
Truth Map + sichtbare Zustände + Artefakt A3

### Block 3
Hauptworkflow + Kontextmodell + Artefakt A4

### Block 4
Web/Mobile/API Truth Audit + Artefakt A5

### Block 5
Rollen / Proaktivität / Persistenz + Artefakte A6/A8

### Block 6
Code / Build / Contracts / Stubs + Artefakt A7

### Block 7
Gap-Konsolidierung + Done-Definition + Artefakte A8/A9

---

## 11. Abschlussregel

Die Gesamtanalyse ist erst dann abgeschlossen, wenn sie nicht nur sagen kann:

- was kaputt ist
- was fake ist
- was fehlt

sondern auch:

- **welcher Zustand jetzt wahr ist**
- **welche Lücken noch objektiv offen sind**
- **welche Reihenfolge notwendig ist, um Eidolon real fertig zu machen**
- **welcher Nachweis erbracht wurde, dass etwas wirklich fertig ist**
