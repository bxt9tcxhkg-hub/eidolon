# Bot Role Requirements

## Zweck
Dieses Dokument definiert die Mindestanforderungen an jede neue Bot-Rolle in Eidolon.

## Grundsatz
Keine neue Bot-Rolle ohne belastbare Stellenbeschreibung.

## Pflichtfelder jeder Bot-Rolle
1. **Name**
2. **Zweck**
3. **Verantwortungsbereich**
4. **Kernaufgaben**
5. **Nicht-Zuständigkeiten**
6. **Aktivierungslogik**
7. **Autonomierahmen**
8. **Hierarchie / Berichtslinie**
9. **Kontextquellen**
10. **Erfolgskriterien**
11. **Lebensdauer**
12. **Existenzbegründung**

## Erklärungsanforderung
Jede Rolle muss so beschreibbar sein, dass ein Laie versteht:
- warum sie existiert
- was sie tut
- was sie nicht tut
- warum dafür nicht einfach Eidolon selbst reicht

## Mindestanforderungen je Feld
### Zweck
Ein klarer Satz. Wenn der Zweck nicht in einem Satz formulierbar ist, ist die Rolle noch nicht reif.

### Verantwortungsbereich
Muss In-Scope und Out-of-Scope enthalten.

### Kernaufgaben
Keine abstrakten Floskeln. 3 bis 7 konkrete Kernaufgaben sind der Richtwert.

### Nicht-Zuständigkeiten
Pflichtfeld. Ohne klare Grenzen wächst die Rolle unkontrolliert.

### Aktivierungslogik
Die Rolle braucht klare Trigger. Sonst bleibt sie tot oder wird aufdringlich.

### Autonomierahmen
Muss trennen zwischen:
- darf autonom
- darf vorbereiten / empfehlen
- muss Eidolon eskalieren
- muss den Nutzer fragen

### Hierarchie
Muss direkte Berichtslinie und erlaubte Delegation klären.

### Erfolgskriterien
Wenn Erfolg nicht prüfbar ist, ist die Rolle strukturell schwach.

### Existenzbegründung
Ohne klare Begründung keine neue Rolle.

## Negativtest
Eine neue Bot-Rolle darf **nicht** angelegt werden, wenn:
- der Zweck unklar ist
- ein bestehender Bot die Aufgabe sauber tragen kann
- die Aufgabe nur einmalig ist
- der Koordinationsaufwand größer als der Nutzen ist
- keine klaren Nicht-Zuständigkeiten formulierbar sind
- keine Erfolgskriterien formulierbar sind
- die Hierarchie unklar bleibt
- die Rolle nur aus Stil-, Persona- oder Agentenästhetikgründen attraktiv wirkt

## Sichtbarkeitszusatz
Für dauerhafte oder nutzernahe Rollen sollte zusätzlich geklärt werden:
- direkter Gegenüber-Bot ja/nein
- eigene Oberfläche ja/nein
- nur Statussichtbarkeit oder echte Gesprächssicht

## Verbindlicher Prüfsatz
Eine Bot-Rolle ist nur dann gut, wenn sofort verständlich ist:
- warum sie existiert
- was sie verantwortet
- was sie nicht darf
- warum ihr Nutzen den zusätzlichen Strukturaufwand rechtfertigt
