# EIDO-001 — Rollenstatus-Drift im `eidolon-core`

- **ID:** `EIDO-001`
- **Titel:** `eidolon-core` wurde als direktes Gegenüber definiert, aber als Background-Rolle ausgeliefert
- **Primärkategorie:** `drift`
- **Severity:** `S0`
- **Status:** `verified`
- **Bereich:** `roles`
- **Surface:** `api`
- **Gefunden in Block:** `A, B, E`

---

## Claim
> Eidolon ist das direkte Gegenüber des Nutzers und die aktive zentrale Instanz.

## Reality
Vor der Korrektur lieferte `/bots/roles` für `eidolon-core`:
- `direct_user_counterpart: true`
- aber zugleich `visibility: "background"`
- und `instantiation_policy: "explicit_approval"`

Das widersprach Produktidentität und Rollenmodell.

## Warum das problematisch ist
Das System behauptete ein zentrales direktes Gegenüber zu sein, markierte dieselbe Rolle aber im Live-State wie eine Hintergrundrolle. Das ist ein Produktwahrheitsbruch im Kernmodell.

---

## Evidence

### Quelle(n)
- `data/user/bot_roles.json`
- `python/eidolon/bots/role_registry.py`
- `/bots/roles`

### Direkter Beleg vor Fix
```text
"direct_user_counterpart": true
"visibility": "background"
"instantiation_policy": "explicit_approval"
```

### Reproduktion
1. `GET /bots/roles`
2. `eidolon-core` inspizieren
3. Widerspruch zwischen Gegenüber-Rolle und Background-Markierung sehen

---

## Klassifikation

### Wahrheitstyp aktuell
- [x] derived_honest
- [ ] fake
- [ ] contaminated

### Produktauswirkung
- [x] Produktlüge / Vertrauensbruch
- [x] Rollen-/Kontextmodell falsch

---

## Root Cause
Persistierte Altwerte in `bot_roles.json` wurden beim Laden nicht gegen die neuen Default-Rollenregeln normalisiert.

## Fix Required
- [x] Code ändern
- [x] Test ergänzen

## Konkrete Änderung
- `python/eidolon/bots/role_registry.py`
  - `_ensure_default_templates()` erweitert
  - vorhandene Rollen werden jetzt gegen Default-Definitionen angereichert
  - `eidolon-core` wird auf `visibility=direct` und `instantiation_policy=always_on` gehärtet

---

## Verifikation

### Pflichtchecks
- [x] Test ergänzt
- [x] Syntax ok
- [x] Live-Endpoint geprüft

### Verifikationsbelege
```text
pytest: test_bot_roles_endpoint_exposes_templates_without_claiming_they_are_active
11 passed, 1 warning

Live /bots/roles:
"visibility":"direct"
"instantiation_policy":"always_on"
```

### Done When
`/bots/roles` liefert `eidolon-core` konsistent als direkte aktive Hauptrolle aus.

---

## Abschluss

- **Fix Commit / Änderung:** lokale Codeänderung in `role_registry.py`
- **Verifiziert am:** 2026-08-25
- **Rest-Risiko:** `low`
- **Follow-up nötig:** UI-Flächen prüfen, ob sie diese Rollenwahrheit auch sichtbar machen
