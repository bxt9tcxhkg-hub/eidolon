# EIDO-025 — Terminal-CLI muss Geräte-Pairing real bedienen können

- **ID:** `EIDO-025`
- **Titel:** Terminal-Nutzung existierte, aber ohne echte Pairing-/Entpairing-Befehle
- **Status:** `verified`
- **Severity:** `S2`
- **Bereiche:** `cli`, `mesh`, `terminal`, `truth-hardening`

---

## Nutzerbedarf
Nach der Frage, ob Eidolon im Terminal nutzbar ist, war der Stand zwar ehrlich benannt, aber unvollständig:

- `chat` funktionierte
- `devices` funktionierte
- `diagnose` funktionierte
- für Pairing/Entpairing gab es im Terminal keinen echten Produktpfad

---

## Root Cause
Die Rust-CLI `eidolon` war nur auf vier Subcommands begrenzt:

- `serve`
- `chat`
- `devices`
- `diagnose`

Für Mesh-Geräteverwaltung fehlten echte Befehle gegen die vorhandenen Runtime-Endpunkte.

---

## Fix
Die CLI wurde um echte Runtime-Subcommands erweitert:

- `eidolon paired --port 8002`
  - liest `GET /mesh/pairing/paired`
- `eidolon pair --port 8002`
  - ruft `POST /mesh/pairing/create` auf
- `eidolon unpair <peer_id> --port 8002`
  - ruft `DELETE /mesh/pairing/paired/{peer_id}` auf

Kein Platzhaltertext: Die CLI spricht direkt die laufende Eidolon-Runtime über HTTP an und gibt die echte JSON-Antwort zurück.

---

## Verifikation
```text
python -m pytest -q      -> 39 passed, 1 warning
cargo build -p eidolon-cli --release -> erfolgreich
node --check             -> Inline-Skripte + workspace-ui.js OK
```

Live-CLI-Dogfood:
1. `eidolon --help` zeigte `paired`, `pair`, `unpair`.
2. `eidolon paired --port 8002` lieferte echte gekoppelte Geräte.
3. `eidolon pair --port 8002` erzeugte einen echten Pairing-Code.
4. Code wurde über Runtime-API mit einem temporären Dogfood-Gerät akzeptiert.
5. `eidolon unpair cli-unpair-dogfood --port 8002` entfernte das Gerät wieder real.
6. Zustand wurde anschließend auf den Vorzustand zurückgesetzt.

---

## Schluss
Eidolon ist jetzt nicht nur lesend, sondern auch für Pairing-/Entpairing-Flows im Terminal nutzbar. Das schließt die offensichtliche CLI-Lücke, die nach der Terminal-Frage noch offen war.
