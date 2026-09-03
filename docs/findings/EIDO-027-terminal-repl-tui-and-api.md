# EIDO-027 — Terminal-Restpunkte REPL, TUI und allgemeiner Runtime-Zugriff real ausgebaut

- **ID:** `EIDO-027`
- **Titel:** Terminal-Nutzung hatte noch keine REPL, keine TUI und keinen allgemeinen Zugriff auf restliche Runtime-Endpunkte
- **Status:** `verified`
- **Severity:** `S2`
- **Bereiche:** `cli`, `repl`, `tui`, `terminal`, `runtime`

---

## Offene Restpunkte
Die vorherigen ehrlichen Einschränkungen waren:

1. keine REPL
2. keine TUI / ncurses-artige Terminal-Oberfläche
3. keine breite Terminal-Abdeckung jenseits einzelner expliziter Commands

---

## Fix
### 1) Reale REPL
Neuer Befehl:
```bash
eidolon repl --port 8002
```

Die REPL bleibt im Terminal offen und verarbeitet echte Runtime-Kommandos wie:
- `chat ...`
- `projects`
- `project-create ...`
- `goals`
- `goal-transition ...`
- `settings ...`
- `api GET /path`

### 2) Reale TUI
Neuer Befehl:
```bash
eidolon tui --port 8002
```

Die TUI läuft im Alternate Screen über `crossterm` und zeigt echte Runtime-Daten in Tabs:
- Chat
- Status
- Geräte
- Projekte
- Ziele
- Settings
- Hilfe

Interaktionen sind real, nicht nur Anzeige:
- Chat senden
- Pairing-Code erzeugen
- Geräte entkoppeln
- Projekte anlegen/löschen
- Ziele anlegen/aktivieren/pausieren/löschen
- Settings ändern/zurücksetzen

### 3) Allgemeiner Runtime-Zugriff
Neuer Befehl:
```bash
eidolon api <METHOD> <PATH> [JSON] --port 8002
```

Damit ist die CLI nicht mehr auf fest verdrahtete Subcommands beschränkt, sondern kann beliebige vorhandene Runtime-Endpunkte direkt ansprechen.

---

## Verifikation
```text
python -m pytest -q      -> 42 passed, 1 warning
cargo build -p eidolon-cli --release -> erfolgreich
node --check             -> Inline-Skripte + workspace-ui.js OK
```

Live-Dogfood:
1. REPL gestartet, `projects` und `chat Antworte nur mit OK.` eingegeben, echte Antworten erhalten.
2. TUI gestartet, auf Geräte-Tab gewechselt, echten Pairing-Code erzeugt, sauber beendet.
3. Offene TUI-Pairing-Codes danach aktiv über `/mesh/pairing/reject` bereinigt.
4. Generischer API-Zugriff geprüft:
   - `eidolon api GET /certificates --port 8002`
   - lieferte echte Zertifikatsdaten.
5. Frühere CLI-Dogfood-Zustände (Projekt, Ziel, Theme, Pairings) blieben bereinigt.

---

## Schluss
Die drei explizit benannten Terminal-Restpunkte wurden real ausgebaut:
- REPL existiert
- TUI existiert
- allgemeiner Runtime-Zugriff per Terminal existiert

Damit ist Eidolon im Terminal nicht mehr nur ein Satz loser Einzelkommandos, sondern besitzt jetzt eine echte interaktive Shell, eine echte Terminal-Oberfläche und einen allgemeinen Runtime-Zugriffspfad.
