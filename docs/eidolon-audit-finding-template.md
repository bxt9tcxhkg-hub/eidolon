# Eidolon Audit Finding Template

Verwende **einen Eintrag pro Befund**. Keine Sammelbefunde.

---

## Kopf

- **ID:** `EIDO-###`
- **Titel:**
- **Primärkategorie:** `fake | placebo | hallucination | placeholder | missing_part | defect | drift`
- **Severity:** `S0 | S1 | S2 | S3`
- **Status:** `open | fixing | blocked | verified | closed`
- **Bereich:** `product_identity | workflow | roles | context | suggestions | projects | healing | mesh | ui | persistence | runtime | build | docs`
- **Surface:** `web | mobile | api | runtime | storage | rust | python | docs`
- **Gefunden in Block:** `A | B | C | D | E | F | G | H | I`

---

## Behauptung vs Realität

### Claim
> Welche explizite oder implizite Behauptung macht Eidolon hier aktuell?

### Reality
> Was ist tatsächlich der Fall?

### Warum das problematisch ist
> Warum ist das ein Vertrauensbruch, Kernblocker oder Qualitätsmangel?

---

## Evidence

### Quelle(n)
- Datei:
- Endpoint:
- UI-Surface:
- Persistenzdatei:
- Runtime-Output:

### Direkter Beleg
```text
Hier echte Antwort, echter Fehler, echter Codepfad oder echte Beobachtung einfügen.
```

### Reproduktion
1.
2.
3.

---

## Klassifikation

### Wahrheitstyp aktuell
- [ ] live
- [ ] derived_honest
- [ ] default_marked
- [ ] unavailable_explicit
- [ ] contaminated
- [ ] fake

### Produktauswirkung
- [ ] Produktlüge / Vertrauensbruch
- [ ] Hauptworkflow blockiert
- [ ] Rollen-/Kontextmodell falsch
- [ ] UI sagt etwas Falsches
- [ ] Persistenz kontaminiert Live-State
- [ ] Technischer Defekt ohne Produktlüge
- [ ] Nur Politur

---

## Fixdefinition

### Root Cause
> Was ist die eigentliche Ursache, nicht nur das Symptom?

### Fix Required
- [ ] Code ändern
- [ ] Persistenz bereinigen
- [ ] UI ehrlich machen
- [ ] Fallback entfernen
- [ ] Dokumentation korrigieren
- [ ] Test ergänzen
- [ ] Build/Contract reparieren

### Konkrete Änderung
> Welche Dateien / Routen / Komponenten müssen geändert werden?

---

## Verifikation

### Pflichtchecks
- [ ] passender Test vorhanden oder ergänzt
- [ ] Syntax/Compile ok
- [ ] Live-Endpoint geprüft
- [ ] UI-Interaktion geprüft
- [ ] Persistenz-/Quellenlage geprüft

### Verifikationsbelege
```text
pytest / cargo check / node --check / live HTTP responses / UI-Evidenz
```

### Done When
> Objektiv messbare Abschlussbedingung.

---

## Abschluss

- **Fix Commit / Änderung:**
- **Verifiziert am:**
- **Verifiziert durch:**
- **Rest-Risiko:** `none | low | medium | high`
- **Follow-up nötig:**
