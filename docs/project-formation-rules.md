# Project Formation Rules

## Zweck
Dieses Dokument definiert, wann aus Gespräch ein strukturierter Arbeitskontext, ein Projektkandidat oder ein aktives Projekt wird.

## Zustände
### `chat_topic`
Ein Thema ist im Gespräch präsent, aber noch nicht stark genug für strukturierte Fortsetzung.

### `project_candidate`
Ein Thema ist mehr als bloßer Chat, aber noch nicht reif genug für voll autonomes Projektverhalten oder einen eigenen dauerhaften Projekt-Bot.

### `active_project`
Ein Thema ist zu einem eigenständigen, fortsetzungsfähigen Arbeitsrahmen geworden.

## Weg 1: Geklärter Auftrag
Ein Projekt oder Projektkandidat darf entstehen, wenn aus dem Gespräch klar geworden ist:
- worauf hingearbeitet wird
- warum Fortsetzung sinnvoll ist
- welche grobe Richtung gilt

## Weg 2: Proaktive Entstehung
Eidolon darf einen Projektkandidaten auch dann erzeugen, wenn noch nicht alle Inputs vollständig sind, aber:
- bei einem Thema wiederkehrend Hilfe nötig ist
- das Thema nicht nur einmalig ist
- persistenter Kontext dem Nutzer voraussichtlich nützt

## Was proaktive Entstehung nicht darf
- ein unvollständiges Thema als fertiges Projekt ausgeben
- fehlende Kernentscheidungen still erfinden
- einen dauerhaften Projekt-Bot ohne Freigabe anlegen

## Übergangslogik
### `chat_topic` → `project_candidate`
Wenn mindestens eines gilt:
- wiederkehrender Hilfebedarf
- klarer Bedarf an Verlauf oder Nachverfolgung
- erkennbare Fortsetzung über eine Einmalantwort hinaus
- ein arbeitsorientiertes Vorhaben in der Nachricht, auch ohne LLM: deterministische Extraktion plus sichtbare Bestätigung

### `project_candidate` → `active_project`
Wenn genug Struktur vorhanden ist, um:
- Ziel und groben Scope zu benennen
- nächsten Arbeitsweg abzuleiten
- sinnvolle Oberfläche und Zuständigkeiten zuzuordnen

## Projektwechsel vs. Exkurs
### Exkurs
Ein anderes Projekt wird nur erwähnt, verglichen oder kurz referenziert.

### Projektwechsel
Ein anderes Projekt wird zum primären Arbeitskontext für Denken, Entscheiden oder Ausführen.

Kernregel:
> Erwähnung ist kein Wechsel. Bearbeitung ist ein Wechsel.

## Sichtbarkeitsregel
Eidolon darf Projektwechsel zunächst im Hintergrund erkennen, muss ihn aber sichtbar machen, bevor falsche Zuordnung oder falsche Ausführung entsteht.

## Ergebnisregel
Projektbildung ist kein rein sprachliches Labeling, sondern eine Arbeitsentscheidung:
- Kontext bleibt erhalten
- spätere Rückkehr wird möglich
- passende Oberfläche kann entstehen
- Rollenbildung wird vorbereitet

## Board-Karten aus dem Vorhaben
Nach sichtbarer Bestätigung (`project_candidate` → `active_project`) entstehen Planungselemente aus dem Nachrichtentext, nicht aus einem Domänen-Paket.

- Titel und Split kommen aus dem genannten Vorhaben (Fakten, Bedingungen, offene Punkte)
- Bedingungen (etwa eigenes Bad, genannte Kürzel) hängen an der passenden Karte (Notizen/Metadaten), ohne erfundene Orte oder Ausstattung
- Status ist `planned`, solange der Text kein Tor impliziert (`erst nach`, `ohne Freigabe`, …)
- Karten bleiben über die bestehenden Projekt-APIs umbenennbar, verschiebbar und streichbar
- Erneutes Seed ist idempotent: vorhandene `slot:*`- oder gleiche Titel werden nicht verdoppelt; Nutzerkarten ohne `seed:vorhaben` bleiben unangetastet
