# EIDO-005 — `workspaces/context` leitete nächsten Schritt ohne Live-Signale ab

- **ID:** `EIDO-005`
- **Titel:** Kontextmodell lieferte `next_step`/`next_transition`, obwohl keine Themen oder Projekte vorlagen
- **Primärkategorie:** `placebo`
- **Severity:** `S1`
- **Status:** `verified`
- **Bereich:** `workflow`
- **Surface:** `api`, `ui`
- **Gefunden in Block:** `C, D`

---

## Claim
> Der nächste Kontextübergang leite sich aus realen Gesprächssignalen ab.

## Reality
Vor dem Fix lieferte `/workspaces/context` bei komplett leerem Live-Zustand trotzdem:
- `current_context_state: "chat_topic"`
- `next_transition: "structure_topic_into_candidate"`
- `next_step: "Aus Gesprächssignalen einen klaren Projektkandidaten ... formen."`

Gleichzeitig waren aber:
- `chat_topic_count: 0`
- `project_candidate_count: 0`
- `active_project_count: 0`
- `topic_labels: []`
- `projects: []`

## Warum das problematisch ist
Das war ein Placebo-Muster: Das System formulierte einen semantischen nächsten Projektschritt, obwohl keine realen Signale existierten, auf die sich dieser Schritt stützte.

---

## Evidence

### Quelle(n)
- `python/eidolon/workspaces/registry.py`
- `GET /workspaces/context`
- Live-UI „Projektflächen → Arbeitskontext"

### Direkter Beleg vor Fix
```text
/workspaces/context:
"chat_topic_count":0
"topic_labels":[]
"next_transition":"structure_topic_into_candidate"
"next_step":"Aus Gesprächssignalen einen klaren Projektkandidaten ... formen."
```

---

## Root Cause
`build_context_model()` erzeugte den nächsten Schritt aus einer Else-Kette, ohne zwischen echtem `chat_topic` und komplett leerem Zustand zu unterscheiden.

## Fix Required
- [x] Code geändert
- [x] Test ergänzt
- [x] Live-Endpoint geprüft
- [x] Live-UI geprüft

## Konkrete Änderung
- `python/eidolon/workspaces/registry.py`
  - neuer expliziter Zustand `no_live_context`
  - `current_phase: await_input`
  - `next_transition: null`
  - `approval_state: awaiting_live_input`
  - ehrlicher `next_step`: auf neue Live-Signale warten
- `tests/test_web_ui_contracts.py`
  - neuer Vertragstest für echten Leerzustand

---

## Verifikation

### Verifikationsbelege
```text
pytest:
14 passed, 1 warning

Live /workspaces/context:
"current_context_state":"no_live_context"
"current_phase":"await_input"
"next_transition":null
"next_step":"Kein aktiver Gesprächs- oder Projektkontext vorhanden. Auf neue Live-Signale warten."
```

### UI-Beleg
Live in „Projektflächen“ geprüft:
- Kontextzustand: `no_live_context`
- Nächster Übergang: `—`
- Projektliste: `Keine Projekte`

---

## Abschluss
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
- **Follow-up nötig:** Nur, falls künftig echte Topic-Signale feiner klassifiziert werden sollen
