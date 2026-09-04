# Eidolon Specification

> Status: verbindliche Produktspezifikation auf Basis der bisher geklärten Produktentscheidungen. Dieses Dokument beschreibt **Soll-Regeln** für Eidolon. Es behauptet **nicht**, dass diese Regeln bereits implementiert sind.

## Zweck
Diese Spezifikation definiert Eidolon als Produktgrundlage ohne Placebos, Fake-Funktionalität oder aspirative Erfolgsbehauptungen. Sie legt fest:
- was Eidolon ist
- wie es denken, strukturieren und handeln soll
- wie Projekte, Bots und Oberflächen zusammenhängen
- welche Regeln systemweit bindend sind

## Dokumentstruktur
1. [Produktidentität](./eidolon-product-identity.md)
2. [Kernworkflow](./eidolon-core-workflow.md)
3. [Projektentstehungslogik](./project-formation-rules.md)
4. [Autonomie- und Sicherheitsvertrag](./eidolon-autonomy-contract.md)
5. [Bot-Organisationsmodell](./bot-organization-model.md)
6. [Anforderungen an Bot-Rollen](./bot-role-requirements.md)
7. [UI- und Workspace-Architektur](./eidolon-ui-workspace-architecture.md)

## Verbindliche Gesamtprinzipien
1. **Eidolon ist das zentrale Hauptsystem.**
2. **Chat ist die feste Startoberfläche.**
3. **Adaptive Oberflächen sind erlaubt, semantische Beliebigkeit nicht.**
4. **Bots sind organisatorische Rollen, keine dekorativen Personas.**
5. **Autonomie ist erlaubt, aber nur innerhalb klarer Leitplanken und mit sichtbarer Verantwortlichkeit.**
6. **Dauerhafte Strukturänderungen entstehen nicht stillschweigend.**
7. **Keine Placebos, keine Fake-Daten, keine Scheinfunktionen.**

## Was diese Spezifikation bewusst nicht tut
- keine Behauptung, dass die aktuelle Codebasis diese Regeln schon erfüllt
- keine Implementierungsdetails erfinden, die nicht geklärt wurden
- keine UI-Mockups als fertige Produktwahrheit ausgeben
- keine Domänen-Hubs hart vorschreiben
- keine fest verdrahteten Domänen-Pakete (Training, Instagram, Reise und vergleichbare Beispiele sind nur Illustrationsfälle)

## Verbindlicher Prüfsatz
Wenn eine spätere Produkt- oder Implementierungsentscheidung diesen Dokumenten widerspricht, gilt:
- **Produktklarheit vor Sonderfall**
- **semantische Konsistenz vor visueller Vielfalt**
- **echte Nutzbarkeit vor Demo-Eindruck**
