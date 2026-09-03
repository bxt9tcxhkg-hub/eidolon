# EIDO-028 — System-Metrics und System-Storage-Endpunkte geprüft

- **ID:** `EIDO-028`
- **Titel:** System-Metrics und System-Storage-Endpunkte waren noch nicht geprüft
- **Status:** `verified`
- **Severity:** `S3`
- **Bereiche:** `runtime`, `api`, `truth-hardening`

---

## Offener Punkt
Im Worklog, Block B standen die beiden Punkte noch offen:
- `/system/metrics`
- `/system/storage`

Die API-Endpunkte existierten, aber es wurde noch nicht geprüft, ob sie echte Daten liefern oder Platzhalter.

---

## Prüfergebnis
Live gegen die laufende Runtime:

### `/system/metrics`
Liefert echte Daten:
- Uptime
- Python-Version
- Plattform
- HTTP/QUIC-Port
- Prozess-Memory, CPU, Threads (via psutil)
- System-CPU, RAM, Disk (via psutil)

### `/system/storage`
Liefert echte Daten:
- Backups: 23.688 Dateien, 1.48 GB
- Autonomy: 1 Datei
- Mesh: 6 Dateien
- User: 18 Dateien

---

## Verifikation
```text
python -m pytest -q      -> 42 passed, 1 warning
cargo check --workspace  -> erfolgreich
node --check             -> Inline-Skripte + workspace-ui.js OK
```

Live-HTTP gegen beide Endpunkte lieferte echte Werte.

---

## Schluss
Beide Endpunkte sind echt, liefern reale Systemdaten und sind jetzt im Worklog als geprüft markiert.
