# EIDO-009 — Chat-Test kontaminierte `interaction_log.jsonl` und damit Topic-/Proaktivitätsquellen

- **ID:** `EIDO-009`
- **Titel:** Test-Probe wurde als Live-Chatquelle aufgezeichnet
- **Primärkategorie:** `contaminated`
- **Severity:** `S0`
- **Status:** `verified`
- **Bereich:** `proactivity`, `persistence`, `tests`
- **Surface:** `api`, `data`
- **Gefunden in Block:** `F, G, I`

---

## Claim
> Topic Attention und proaktive Vorschläge leiten sich nur aus realen Live-Signalen ab.

## Reality
`interaction_log.jsonl` enthielt 14 Einträge mit dem Testsatz:
- `Antworte nur mit dem Wort OK.`

Diese Einträge trugen die Quelle `chat` und konnten daher als scheinbar reale Gesprächssignale in die Topic-/Proaktivitäts-Pipeline eingehen.

---

## Fix
1. `tests/test_chat_runtime.py`
   - sendet jetzt `source: test-chat-runtime`
   - restauriert den ursprünglichen `interaction_log.jsonl`-Zustand im `finally`
2. `python/agent_server.py`
   - `/chat` akzeptiert jetzt optional `source` und loggt nicht mehr blind immer `chat`
3. Bestehende Kontamination bereinigt
   - Backup angelegt:
     `C:/Users/muham/eidolon/data/backups/interaction_cleanup_20260825T131149Z/interaction_log.jsonl`
   - 14 Probe-Zeilen aus dem Live-Log entfernt
4. Topic-Attention neu berechnet
   - `interaction_count: 0`
   - `topics: []`

---

## Verifikation
```text
pytest: 16 passed, 1 warning
```

Live / Dateien:
- `data/user/interaction_log.jsonl` ist leer
- `data/user/topic_attention.json` zeigt `interaction_count: 0`
- `data/user/proactive_assistance.json` zeigt `suggestions: []`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
- **Follow-up nötig:** Nur falls weitere Testpfade Chat-ähnliche Quellen erzeugen
