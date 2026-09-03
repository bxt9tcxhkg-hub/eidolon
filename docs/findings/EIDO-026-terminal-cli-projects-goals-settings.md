# EIDO-026 — Terminal-CLI muss Projekte, Ziele und Einstellungen real bedienen

- **ID:** `EIDO-026`
- **Titel:** Terminal-CLI konnte nach Pairing/Unpairing noch keine Projekte, Ziele und Einstellungen real verwalten
- **Status:** `verified`
- **Severity:** `S2`
- **Bereiche:** `cli`, `projects`, `autonomy`, `settings`, `terminal`

---

## Offene Lücke
Nach `EIDO-025` konnte die CLI bereits:

- `chat`
- `devices`
- `diagnose`
- `paired`
- `pair`
- `unpair`

Aber noch nicht die übrigen zentralen Runtime-Flächen im Terminal bedienen:

- Projekte
- Autonomie-Ziele
- Einstellungen

---

## Fix
Die Rust-CLI `eidolon` wurde um echte Runtime-Subcommands erweitert:

### Projekte
- `eidolon projects --port 8002`
- `eidolon project-create <title> --description ... --domain ... --port 8002`
- `eidolon project-delete <project_id> --port 8002`

### Ziele
- `eidolon goals --port 8002`
- `eidolon goal-create <title> --description ... --category ... --priority ... --step ... --port 8002`
- `eidolon goal-transition <goal_id> <status> --port 8002`
- `eidolon goal-delete <goal_id> --port 8002`

### Einstellungen
- `eidolon settings [area] --port 8002`
- `eidolon settings-set <area> <key> <value> --port 8002`
- `eidolon settings-reset <area> --port 8002`

Die Befehle sprechen direkt die vorhandenen FastAPI-Endpunkte an. Keine simulierte Terminal-Logik, keine lokalen Attrappen.

---

## Verifikation
```text
python -m pytest -q      -> 40 passed, 1 warning
cargo build -p eidolon-cli --release -> erfolgreich
node --check             -> Inline-Skripte + workspace-ui.js OK
```

Live-CLI-Dogfood:
1. `eidolon --help` zeigte alle neuen Commands.
2. Projekt wurde per `project-create` real angelegt und per `projects` wieder sichtbar.
3. Ziel wurde per `goal-create` real angelegt, per `goal-transition ... active` in `active` überführt und danach gelöscht.
4. `settings ui` las echte UI-Einstellungen.
5. `settings-set ui theme "light"` änderte den echten Setting-Wert.
6. Der Theme-Wert wurde anschließend auf den ursprünglichen Zustand zurückgesetzt.
7. Das temporäre Projekt und das temporäre Ziel wurden wieder gelöscht.

Beobachtetes Ergebnis:
```json
{"help_has_new_commands": true, "project_created": true, "project_visible_after_create": true, "goal_created": true, "goal_transitioned_to_active": true, "settings_ui_read_ok": true, "theme_set_to_light": true, "theme_restored": true, "goal_deleted": true, "project_deleted": true, "project_cleanup_ok": true, "goal_cleanup_ok": true}
```

---

## Schluss
Eidolon ist im Terminal jetzt nicht mehr nur für Chat und Geräteverwaltung nutzbar, sondern auch für reale Projekt-, Ziel- und Settings-Flows gegen die laufende Runtime.
