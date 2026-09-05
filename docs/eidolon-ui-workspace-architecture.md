# Eidolon UI and Workspace Architecture

## Zweck
Dieses Dokument definiert, wie Eidolon adaptive Arbeitsoberflächen erzeugen darf, ohne in UI-Beliebigkeit oder semantisches Chaos zu kippen.

## Grundsatz
Eidolon soll **keine starre Einheitsoptik** haben.

Aber:
> **Die Oberfläche darf adaptiv sein. Die Semantik darf es nicht.**

Das bedeutet:
- unterschiedliche Arbeitsflächen sind erlaubt
- unterschiedliche Modulkomposition ist erlaubt
- unterschiedliche visuelle Dichte ist erlaubt
- unterschiedliche Primärdarstellungen je Problem sind erlaubt

Nicht erlaubt ist:
- wechselnde Bedeutung von Zuständen
- versteckte Kontextwechsel
- unklare Verantwortlichkeit
- inkonsistente Freigabelogik
- Vermischung von Vorschlag, Entscheidung, Aufgabe und Ergebnis

## Arbeitsmodi statt Domänen-Hubs
Eidolon soll Oberflächen nicht primär nach Themenkatalogen bauen, sondern nach Arbeitsmodi.
Training, Instagram oder Reise sind nur Beispiele für beliebige Vorhaben. Es darf **keine** fest verdrahteten Domänen-Pakete, Domänen-Tabs oder Spezial-UIs dafür geben. Karten und Widgets sind ein **generisches Gerüst** (Slots und Typen), das Kernel und Workspace speisen.

Verbindliche Arbeitsmodi sind:
1. Gespräch / Einstieg
2. Verständnis / Konzeptbildung
3. Projektführung / Ausführung
4. Review / Freigabe
5. Status / Organisation

## Erlaubte Kernbausteine
Eidolon soll aus einem begrenzten Satz starker UI-Bausteine zusammensetzen:
- Chat
- Tabelle
- Liste / Checkliste
- Detailansicht
- Formular / strukturierte Eingabe
- Kalender / Timeline
- Ziel- / Fortschrittsmodul
- Karten- / Routenmodul
- Recherche- / Quellenmodul
- Review- / Freigabemodul
- Organisations- / Statusmodul

## Kompositionsregel
Workspace-Komposition folgt Problemstruktur, nicht Trend oder bloßer Optik.

Beispiele:
- Inventarproblem → Tabelle + Detail + Status + Fristen
- Trainingsproblem → Ziel + Kalender + Verlauf + Karte
- Contentproblem → Recherche + Cluster + Draft + Freigabe + Publishing-Vorbereitung
- Reiseproblem → Profil + Route + Timeline + Optionen + Entscheidungen

## Verbindliche semantische Achsen
Jede Oberfläche muss dieselben Grundfragen eindeutig beantworten:
1. Kontext — worum geht es gerade?
2. Ziel — worauf wird hingearbeitet?
3. Zustand — wo steht das Objekt oder Vorhaben?
4. Verantwortlichkeit — wer ist zuständig?
5. Handlungstyp — Information, Vorschlag, Aufgabe, Entscheidung, Ergebnis?
6. Änderung — was ist neu oder geändert?
7. Freigabegrad — was darf direkt passieren, was braucht Zustimmung?
8. Nächster Schritt — was ist jetzt sinnvoll?

## Sichtbarkeitsregel
Immer sichtbar oder sofort auffindbar sein müssen:
- aktiver Kontext
- aktives Ziel
- aktueller Gesamtzustand
- zuständige Instanz
- nächster sinnvoller Schritt

## Charakter ohne Placebo
Die Kernschale bleibt dunkel. Wärme kommt aus Typografie, Abstand, Radius und einem reicheren Akzent — nicht aus einem erzwungenen Light-Theme und nicht aus einer zweiten Startwand im Chat.

Lebendigkeit im Leerlauf ist erlaubt, wenn sie ehrlich ist:
- ein ruhiger Atem/Puls für „bereit“
- Bereit / Wartet / Als Nächstes nur aus Kernel, Session oder Workspace
- keine erfundenen Läufe, keine Placebo-Fortschrittsbalken

## Harte UX-Regeln
- keine semantisch wichtigen Informationen nur in Hover/Tooltip verstecken
- keine Zustandslogik nur über subtile Farbunterschiede vermitteln
- keine Freigabepflicht nur implizit in Button-Texten verstecken
- keine Verantwortlichkeit nur im Fließtext andeuten
- keine Kontextwechsel stillschweigend durchführen

## Shell-und-Host-Regel
Eidolon braucht eine stabile Kernschale und eine adaptive Host-Fläche.

### Stabile Kernschale
Nicht frei mutierbar:
- Navigation
- Chat-Einstieg
- globale Orientierung
- Systemstatus / Einstellungen

### Adaptive Host-Fläche
Darf sich problemabhängig zusammensetzen, solange sie die semantische Grammatik respektiert.

## Ergebnisregel
Eine gute Eidolon-Oberfläche ist nicht daran zu erkennen, dass sie neu oder spektakulär aussieht, sondern daran, dass sie:
- zum Problem passt
- klare Orientierung gibt
- wenig Klicklast erzeugt
- richtige nächste Schritte sichtbar macht
- mit dem restlichen System semantisch konsistent bleibt

## Verbindlicher Prüfsatz
Wenn eine neue Oberfläche nur deshalb eingeführt wird, weil sie modern aussieht, aber keine klar bessere Arbeitslogik liefert, wird sie nicht Teil des Produktkerns.
