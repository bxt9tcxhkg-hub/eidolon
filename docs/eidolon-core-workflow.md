# Eidolon Core Workflow

## Zweck
Dieses Dokument definiert die verbindliche Hauptschleife, nach der Eidolon Vorhaben vom ersten Gespräch bis zur fortlaufenden Arbeit verarbeitet.

## Hauptschleife
1. **Chat-Einstieg**
2. **Verständnis- und Strukturaufbau**
3. **Kontextklassifikation**
4. **Projektkandidat oder aktives Projekt ableiten**
5. **geeignete Arbeitsoberfläche zusammensetzen**
6. **Bots und Verantwortlichkeiten ableiten, falls nötig**
7. **Arbeit vorbereiten oder ausführen**
8. **Verifikation, Sichtbarkeit und nächste Schritte bereitstellen**

## Phase 1: Chat-Einstieg
Der Chat ist immer die feste Startoberfläche.

Im Chat darf der Nutzer:
- neue Themen beginnen
- bestehende Themen fortsetzen
- zwischen Projekten springen
- Eidolon korrigieren
- Entscheidungen freigeben oder ablehnen

## Phase 2: Verständnis- und Strukturaufbau
Eidolon muss aus dem Gespräch mindestens ableiten:
- Hauptziel
- groben Scope
- relevante Einschränkungen
- ob nur Antwort, laufende Hilfe oder strukturierte Fortsetzung nötig ist

## Phase 3: Kontextklassifikation
Eidolon klassifiziert den aktuellen Gesprächszustand als:
- `chat_topic`
- `project_candidate`
- `active_project`

Zusätzlich unterscheidet Eidolon zwischen:
- Hauptkontext
- Nebenkontext
- Exkurs
- bestätigtem Projektwechsel

## Phase 4: Projektbildung
Ein Projekt kann entstehen durch:
- explizit geklärten Arbeitsauftrag
- proaktiv erkannten wiederkehrenden Hilfebedarf

Nicht jedes Thema wird sofort zu einem aktiven Projekt-Bot. Die Zwischenstufe `project_candidate` ist verbindlich vorgesehen.

## Phase 5: Workspace-Komposition
Eidolon darf den Arbeitsraum problemabhängig zusammensetzen, aber nicht beliebig. Die Wahl der Oberfläche folgt dem Arbeitsmodus:
- Gespräch / Richtungsfindung
- Verständnis / Konzeptbildung
- Projektführung / Ausführung
- Review / Freigabe
- Status / Organisation

## Phase 6: Rollenbildung
Bots entstehen nur, wenn sie echten strukturellen Nutzen bringen.

Typische Fälle:
- temporärer Task-Bot für begrenzte Teilaufgabe
- dauerhafter Projekt-Bot für wiederkehrenden Verantwortungsbereich
- Meta-/Management-Bot nur für Organisationsanalyse, nicht als stiller Machtausbau

## Phase 7: Ausführung
Eidolon oder delegierte Bots arbeiten innerhalb klarer Leitplanken:
- operative Entscheidungen lokal
- strategische Richtungsfragen zurück an Eidolon
- kritische Freigabepunkte sichtbar

## Phase 8: Verifikation und Rückkehr
Jede sinnvolle Arbeitsphase endet mit mindestens diesen sichtbaren Informationen:
- aktueller Kontext
- aktuelles Ziel
- aktueller Zustand
- zuständige Instanz
- nächster sinnvoller Schritt

## Kernregel
Eidolon arbeitet nicht in losen Einzelschritten, sondern in einer zusammenhängenden Schleife aus:
**verstehen → strukturieren → einordnen → organisieren → ausführen → verifizieren → fortsetzen**
