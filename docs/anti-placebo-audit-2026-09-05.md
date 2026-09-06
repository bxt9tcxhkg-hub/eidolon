# Anti-Placebo-Audit — 2026-09-05

**Regel:** Nichts darf Placebo / Placeholder / Fake sein. Keine stillen Lücken, kein Halluzinieren. Entweder echt verdrahtet und wahr, oder ehrlich als nicht verfügbar / nicht verbunden gezeigt. Gilt für UI, APIs, Chat, Settings, LLM, Freigaben und jede Feature-Fläche.

**Scope:** `master` @ `70eabc4`. Zusätzlich offener Draft-PR #11 (`cursor/llm-provider-registry-8680` @ `2bef5c5`). Keine Fixes in diesem Schnitt, außer dass dieser Bericht die Befunde festhält. Nicht mergen.

**Methode:** Code- und Vertragslesung (UI, FastAPI-Routen, Operate, Settings, Healing, Capabilities, Skills). Kein Live-Browser-Dogfood in dieser Umgebung. Bekannte Alt-Findings (EIDO-007, EIDO-021, EIDO-002) wurden gegen den aktuellen Code geprüft, nicht nur dokumentarisch übernommen.

---

## 1. Kritisch — nutzerseitige Lügen / Fake-Success

### K1 — Settings: OpenAI-Login zeigt Erfolg, obwohl kein Login stattfand (`master`)

| | |
|---|---|
| **Datei / Route** | `python/eidolon/web/settings-ui.js` (`triggerOpenAILogin`, `checkOpenAIAuth`); `POST /integrations/openai/login`; `POST /integrations/openai/auth`; `python/eidolon/runtime_service_auth.py` |
| **Nutzer sieht** | Dropdown „OpenAI (Login)“, Button „OpenAI Login starten“, Hinweis „echter Gerätecode-Login … auch auf dem Handy“. Bei `ok` Toast „Login erfolgreich“ bzw. „OpenAI verbunden“. |
| **Wahrheit** | `spawn_openai_device_login()` erzeugt **keinen** Device-Code. Ohne Session kommen weder `session_id` noch `verification_url`/`user_code`. Codex vorhanden, aber nicht eingeloggt → `{ok: True, status: 'manual_login_required', command: 'codex login --device-auth'}`. Die UI wertet `result.ok` als Erfolg. `POST /integrations/openai/auth` setzt immer `ok: True, supported: True` und übernimmt nur den Codex-Status; `checkOpenAIAuth` toastet bei `ok` „OpenAI verbunden“, auch wenn `configured: false`. |
| **Fix-Richtung** | Login-API nur `ok: true`, wenn wirklich eingeloggt. `manual_login_required` / fehlende CLI als Warnung oder Fehler. UI niemals Success-Toast auf `ok` ohne `logged_in`/`configured`. Device-Code entweder echt implementieren oder Button entfernen und nur `codex login` ehrlich anbieten. |

Zusätzlich widerspricht der Settings-Header sich selbst:

- `python/eidolon/web/fragments/index-healing-footer.html`: „OAuth ist in diesem lokalen Runtime-Pfad nicht implementiert.“
- Dieselbe Seite bietet „OpenAI (Login)“ und behauptet API-Key-Anbindung. Die Route `POST /llm/openai/api-key` **existiert auf `master` nicht mehr** (EIDO-021-Drift). `saveOpenAIKey()` postet ins Leere. `load_openai_api_key` / `save_openai_api_key` werden vom Live-LLM-Backend nicht genutzt.

`llm.provider = openai` ist im Schema erlaubt (`settings_schema_llm.py`), im Dropdown unsichtbar. `LLMBackend.complete()` wirft dann ehrlich `LLM-Provider nicht angebunden: openai`. Persistenz und Chat-Pfad sind also inkonsistent: API kann `openai` speichern, Runtime kann es nicht ausführen.

### K2 — Capabilities als verfügbar markiert, obwohl der Check nichts prüft

| | |
|---|---|
| **Datei / Route** | `GET /capabilities`, `GET /health`; `python/eidolon/core/capability_catalog.py`, `capability_checks.py`, `capability_models.py`; UI `dashboard-ui.js`, `execution-ui.js` |
| **Nutzer sieht** | Systemstatus / Laufzeit: grüne Punkte, „Capabilities X/Y“, „Lokales Ollama LLM“ verfügbar, „Skill Runtime“ / „Autonomy background loop“ / „Dateien lesen/schreiben“ verfügbar. |
| **Wahrheit** | Default-`_check_fn` ist `lambda: True`. Damit sind `file.read`, `file.write`, `evidence.store`, `skills.runtime`, `autonomy.loop` **immer** `available: true`. `ollama_available()` ist immer wahr, weil `os.environ.get('OLLAMA_HOST', 'http://localhost:11434')` nie leer ist — kein Ping. `mesh.quic` ist wahr, sobald das Modul importiert; das ist nicht der Listener (`/health.quic_port` kann gleichzeitig `not_wired` sein). `autonomy.loop`: es gibt **keine** Hintergrundschleife; `run_cycle()` läuft nur auf Knopfdruck und aktiviert höchstens ein Ziel. `skills.runtime`: die Live-Chat-Route ruft `SkillRegistry` nicht auf. |
| **Fix-Richtung** | Capability nur `available`, wenn ein echter Probe-Check gilt (Ollama `/api/tags`, QUIC `_running`, Autonomy-Task existiert, Skill-Execute-Pfad verdrahtet). Sonst `available: false` + ehrliches `detail`. Default nicht `True`. |

### K3 — Fähigkeiten-Seite behauptet ausführbare Runtime-Skills

| | |
|---|---|
| **Datei / Route** | Nav „Fähigkeiten“ / `#skills`; `app-shell.js` Subtitle „Aktivierte Werkzeuge und ausführbare Runtime-Fähigkeiten“; `GET /skills`; `healing_skills_routes.py`; `runtime_builtin_skills.py`; toter Katalog `skills/skill_catalog.py` |
| **Nutzer sieht** | Liste mit grünen Punkten: Chat, Runtime-Fakten, System-Info, Goal-Manager, Geräte, Mesh-Send, Notizen, Dateien organisieren — alle `enabled`. |
| **Wahrheit** | Die UI hat keine Ausführen-Buttons (das ist ehrlich), verkauft die Einträge aber als aktive Fähigkeiten. `POST /skills/{name}/enable|disable` mutiert nur die In-Memory-Liste `BUILTIN_SKILLS`, ohne Persistenz und ohne die echte `SkillRegistry`. `skills/plugin.py` hängt an FastAPI-Startup, wird von der Live-App nicht geladen. Katalog-Handler (`file_organizer`, `mesh_send`, `calendar`, `goal_manager`) antworten mit Fake-Success-Strings (`Organisiere: …`, `An {peer}: {message}`), falls jemand sie aufruft. |
| **Fix-Richtung** | Entweder Skills an die Registry + Persistenz + echte Handler binden, oder die Seite als „Katalog, nicht ausführbar“ kennzeichnen und Enable-APIs entfernen bzw. `ok: false` liefern. Grüne Punkte nur für wirklich verdrahtete, getestete Skills. |

### K4 — Freigabe-Tür: Freigeben ändert nur den Run-State, führt die Aktion nicht aus

| | |
|---|---|
| **Datei / Route** | Chat `#chat-decision-summary`, Arbeit `#operate`; `resolveOperateApproval` → `POST /api/v1/runs/{id}/approval/{gate}`; `operate/service_support_actions.py` `resolve_approval`; Seed `workspaces/board_seed.py` + `vorhaben_extract.py` |
| **Nutzer sieht** | Bei Buchungs-/Extern-Vorhaben nach Bestätigen: „Freigeben“ / „Ablehnen“. Nach Freigeben Motion „approved“ und Run geht weiter. Ohne Gate oft nur „Weiter“. |
| **Wahrheit** | Die Tür ist **real persistiert** (Approval-Record, Chat und Arbeit teilen denselben Snapshot). `approved` setzt den Run auf `planning` und schreibt ein Transition-Event. Es gibt **keinen** Executor für `external_write` (keine Buchung, keine Mail, kein HTTP nach außen). „Weiter“ (`advance_run`) schiebt nur die Zustandsmaschine (`understanding → planning → spawning_work → acting → verifying → completed`) ohne Arbeit. Keyword-Gate ist schmal (`buch`, `hotel`, `anrufen`, …). Viele Vorhaben erzeugen deshalb nur „Weiter“ — das erklärt die Live-Beobachtung „nur Weiter“. Ablehnen markiert den Run `failed`, ebenfalls ohne Gegenaktion. Zusätzlich: Chat-`renderChatOperateDoor` zeigt Freigeben/Ablehnen **nur** wenn `pending_approvals` Einträge hat. Operate hat Fallback „Freigabe erneut anfordern“ bei `next_action.kind === 'approval_request'` ohne Gate — Chat nicht. Dann bleibt im Chat oft nur „Weiter“. |
| **Fix-Richtung** | Copy und Next-Action ehrlich machen: „Freigabe notiert — Ausführung ist nicht angebunden“ solange kein Executor existiert. „Weiter“ als „Phase fortschreiben, keine Ausführung“ labeln. Chat dieselbe Fallback-Logik wie Operate. Oder echte, begrenzte Ausführung hinter die Tür legen. Keyword-Liste nicht als vollständige Sicherheitstür verkaufen. |

### K5 — Systemstatus zeigt tote Komponenten als vorhanden (`master` und PR #11)

| | |
|---|---|
| **Datei / Route** | `GET /health` → `runtime_health_payloads.py`; UI `dashboard-ui.js` |
| **Nutzer sieht** | Knowledge Graph „0 Entitäten“ mit grünem Punkt (`available: true`). Mesh-Peers „0 verbunden“ aus `mesh_metrics` (hart 0). Evidence Store „0 verifiziert / 0 blockiert“, `available: true`. `#health-problems` bleibt leer, obwohl `/health.problems` existiert. |
| **Wahrheit** | `knowledge_graph` und `evidence` sind hartcodierte Zeros, nicht aus `KnowledgeGraph` / Evidence-Store gelesen. `mesh_metrics.peer_count` ist nicht `/mesh/peers` oder `/mesh/pairing/paired`. Echte Peer-Zahlen liegen auf anderen Routen. Die Problem-Liste der API wird in der Dashboard-Karte nicht gerendert (nur im Tooltip des lokalen Status-Dots). |
| **Fix-Richtung** | Entweder echte Stats einbinden oder `available: false` / „nicht angebunden“. `#health-problems` aus `d.problems` füllen. Mesh-Zahlen aus dem Peer-Store. |

### K6 — Selbstreflexions-Chat: LLM antwortet, UI zeigt Fehler

| | |
|---|---|
| **Datei / Route** | `python/eidolon/web/chat-ui.js` `sendChat()`; `POST /api/v1/self-reflection/chat`; `operate_api_self_reflection_chat.py`; Envelope `routes/api_response.py` `api_v1_ok` |
| **Nutzer sieht** | Bei „reflektiere…“ / „analysiere dich…“ / „selbstreflexion“: `Fehler: Keine Modellantwort erhalten`. |
| **Wahrheit** | Der Endpoint kann eine echte Modellantwort liefern, wrappt sie aber als `{ok: true, data: {response: …}}`. Die Chat-UI liest nur `r.response` (Top-Level, wie `/chat`). Treffer auf den Self-Reflection-Pfad wirken deshalb wie ein Fehlschlag, obwohl das LLM geantwortet hat. Das ist die sichtbarste Chat-Lüge nach dem (behobenen) EIDO-007-Fake-Success. |
| **Fix-Richtung** | Bei Self-Reflection `r.data.response` lesen oder die API auf `/chat`-Shape (`response` top-level) angleichen. |

---

## 2. Mittel — stille Lücken, halb verdrahtet

### M1 — Settings speichern Werte, die die Runtime nicht nutzt

| Fläche | Nutzer sieht | Wahrheit | Fix-Richtung |
|---|---|---|---|
| Darstellung `theme` / `density` / `language` / `advanced_views` | Speichern-Toast, Badge „gesetzt“ | Persistenz in `settings.json`. Theme läuft über `localStorage` `eidolon-theme` (`loadTheme`); `#theme-icon` existiert nicht. Density/Language/advanced_views haben keinen Leser in der Web-UI. | Settings-Theme an `data-theme` binden oder Felder als „noch ohne Wirkung“ markieren. |
| Netzwerk-Ports | Editierbare Ports, Speichern | Server bindet `EIDOLON_HTTP_PORT` / `HTTP_PORT` aus Env (`agent_server.py`), nicht Settings. | Hinweis „Neustart + Env“ oder Ports wirklich übernehmen. |
| Autonomie `level`, `self_improvement_*`, `cycle_interval_s` | Stufen passiv/proaktiv/voll | Kein Code liest diese Keys. Cycle nur manuell über Ziele-UI. | Felder entfernen oder Engine wirklich steuern. |
| Datenschutz `analytics_enabled`, `retention_days`, `auto_cleanup` | An/Aus, Tage | Nur Schema + Persistenz, keine Cleanup-/Analytics-Pipeline. | Wie oben. |
| LLM `temperature`, `max_tokens`, `offline_mode`, `fallback_chain` auf **master** | Editierbar, speicherbar | `complete_ollama` hardcodiert `temperature: 0.4`. Fallback-Kette wird nicht gelaufen. `offline_mode` ungelesen. Provider `openai` nicht implementiert. | PR #11 adressiert Fallback/Provider; Rest (Temp/Tokens/Offline/Theme) bleibt. |

Toast „Einstellungen gespeichert“ ist für die Datei wahr und für das Produktverhalten oft falsch — klassische stille Lücke.

### M2 — Healing ist verdrahtet, aber Checks/Recovery sind zu grün

| | |
|---|---|
| **Datei / Route** | `GET /healing/status`, `POST /healing/check`; `runtime_lifecycle.py`; `healing_runtime.py`; UI `#healing` „Stabilität“ |
| **Nutzer sieht** | Subtitle „Reale Health-Checks und Wiederherstellungsstatus“. Button „Check ausführen“ → „Healing-Check ausgeführt“. Status `running`. |
| **Wahrheit** | EIDO-002 ist behoben: `SelfHealingService` wird gestartet, Status kommt aus dem Service, nicht mehr hart `ok`. `backup_check` liefert immer `ok: True` (auch bei 0 Backups). `runtime_check` ist immer ok. Recovery (`attempt_targeted_recovery`) hat **keinen** HTTP-Endpunkt; Skills-Recovery gibt `{ok: True, strategy: 'skill_reload_requested'}` ohne Reload. Loop schluckt Exceptions. `POST /healing/check` antwortet immer `{'ok': True, 'cycle': result}`; die UI toastet immer „Healing-Check ausgeführt“ (success), auch wenn `cycle.checks.*.ok` false ist. |
| **Fix-Richtung** | Checks an echte Schwellen binden (Backup-Count, Ollama, Zertifikat). Recovery nicht `ok` ohne Tat. UI an `cycle.checks` koppeln, nicht an Envelope-`ok`. „Wiederherstellung“ nur zeigen, wenn ein Recovery-Pfad existiert. |

### M3 — Helfer / Pods sind Buchhaltung, keine Arbeiter

| | |
|---|---|
| **Datei / Route** | `#pods`; `operate/bridge_workspace_bootstrap.py`; `operate/bridge_actions.py` |
| **Nutzer sieht** | „Aktive Hilfsläufe und ihr realer Zustand“, Karten „Blocker Resolver“ / „Execution Stream“. |
| **Wahrheit** | `spawn_subagent_run` legt Records an (`queued`/`running`/`completed`). Workspace-Mutationen markieren den Pod sofort completed/failed. Kein Prozess, kein LLM-Worker, keine parallele Ausführung. |
| **Fix-Richtung** | Relabel „Protokollierte Hilfsläufe (keine eigenen Prozesse)“ oder echte Worker. Idle-Copy ist schon ehrlich („Keine aktiven Pod-Runs“), die Seite überzeichnet trotzdem. |

### M4 — Chat-Fallback kann wie eine Modellantwort wirken

| | |
|---|---|
| **Datei / Route** | `POST /chat`; `chat_message_routes.py`; `chat_quality_finalize.py` |
| **Nutzer sieht** | Eine arbeitsführende Antwort. EIDO-007 („Antwort erhalten“) ist **weg**; leere/fehlende `response` wird im Frontend als Fehler gezeigt (`chat-ui.js`). |
| **Wahrheit** | Leere Modellantwort wird serverseitig durch `build_grounded_fallback_reply` ersetzt, `ok: true`, `used_fallback: true`. Der Nutzer sieht das Fallback-Flag nicht. Das ist besser als Fake-Success, aber immer noch eine unmarkierte Ersatzstimme. |
| **Fix-Richtung** | Fallback im UI kennzeichnen („Keine Modellantwort — Richtung aus dem Arbeitskontext“). |

### M5 — IA: mehrere Technikflächen erzählen dieselbe Geschichte unterschiedlich

| Label | Route | Drift |
|---|---|---|
| Fähigkeiten | `#skills` | Skill-Katalog, nicht Capabilities |
| Systemstatus → Fähigkeiten | `#dashboard` | Capability-Registry |
| Laufzeit → Laufzeitfähigkeiten | `#execution` | dieselben Capabilities nochmal |
| Stabilität vs Code-Reparatur | `#healing` / `#code` | Healing = Checks; Code = LLM-Mutation. Namen klingen nach Self-Repair-OS |
| Helfer | `#pods` | siehe M3 |
| `advanced_views` | Settings UI | Flag ohne Leser; Advanced-Nav ist immer da |

### M6 — Mesh-Scan und Pairing-Ablehnen schlucken Fehler

`scanMeshPeers()` und `denyPairing()` in `dashboard-ui.js`: `catch (e) {}`. Der Scan-Button sieht aktiv aus; Misserfolg ist unsichtbar.

### M7 — Autonomie-Zyklus tut weniger als der Button sagt

Ziele-UI „Zyklus ausführen“ → `POST /autonomy/cycle` → `run_cycle()` startet höchstens das höchstpriore geplante Ziel und erhöht `cycles_run`. Keine Schritt-Ausführung, kein Healing, kein Code-Fix. „Prüfen & aufräumen“ / „Aus Systemzustand ableiten“ sind echte Store-Mutationen — das Zyklus-Label überzeichnet.

### M8 — PR #11: Chat darf Settings setzen, Wirkung bleibt teilweise Placebo

PR #11 verdrahtet `POST /settings/apply` und Chat-Intent ehrlich (Fragen und „setz das um“ ändern nichts; Secrets werden abgelehnt). Wenn der Nutzer „setze http_port auf 8010“ oder „Thema auf light“ sagt, antwortet der Chat „übernommen“, obwohl Bindung/Theme weiter Env/`localStorage` folgen (M1). Das verschärft die Settings-Lücke, weil jetzt auch der Chat den Erfolg behauptet.

### M9 — Chat-Kontext behauptet Capabilities, die nicht aus dem Katalog kommen

| | |
|---|---|
| **Datei / Route** | `python/eidolon/work_context_contracts.py` `derive_capabilities` |
| **Nutzer / LLM sieht** | `can_analyze`, `can_plan`, `can_summarize`, `can_propose_options` fast immer `true`. `can_execute_actions` wahr, sobald ein Operate-Run oder Workspace aktiv ist. |
| **Wahrheit** | Die Flags sind hardcodiert bzw. nur an Run-Existenz gekoppelt, nicht an Capability-Registry, LLM-Bereitschaft oder einen Executor. Das Modell plant „darf“, obwohl K2/K4 das Gegenteil belegen. |
| **Fix-Richtung** | Flags aus echten Probes + Operate-State ableiten. `can_execute_actions` nur bei angebundenem Executor. |

### M10 — Operate-Aktionsbuttons: Animation ohne Fehler-Feedback

| | |
|---|---|
| **Datei / Route** | `python/eidolon/web/operate-actions-ui.js` |
| **Nutzer sieht** | Nach Klick Motion `continued` / `approved`, als wäre der Call gelungen. |
| **Wahrheit** | Kein `try/catch`, keine Prüfung auf `ok: false`. 400/404 enden als unhandled rejection — keine Notice in Chat/Arbeit. |
| **Fix-Richtung** | Response prüfen, Fehler via `showNotice`, Animation nur bei Erfolg. |

---

## 3. Gering — toter Code / interne Stubs, kaum nutzerseitig

| ID | Ort | Hinweis |
|---|---|---|
| G1 | `python/eidolon/skills/plugin.py`, `skills/runtime.py`, `skills/builtin.py` | Zweiter Skill-Stack, nicht an `agent_server` gehängt. |
| G2 | `python/eidolon/skills/skill_catalog.py` | Fake-Success-Lambdas; tot, solange Registry nicht live ist. Wird kritisch, sobald jemand den Pfad aktiviert. |
| G3 | `WS /ws` | Reines Echo. Footer „Verbinde…“ kommt von `/health`, nicht vom Socket — lokal ehrlich beschriftet. |
| G4 | Rust-Crates | Quarantäne dokumentiert; nicht als zweiter Produktserver verkauft. |
| G5 | `goal_deriver` Rust-Stub-Scanner | Interne Zielableitung, keine User-Lüge. |
| G6 | `VALID_TABS` in `settings_routes.py` | `/tab-settings/{tab}` persistiert freie Areas (`tab_chat` …), UI ruft das nicht auf. `set_area` erlaubt unbekannte Areas ungeprüft. |
| G7 | HUD `Weiter` | Desktop-Nebenfläche; nicht die Web-Starttür. |
| G8 | `health-problems` DOM-Node | Tot, bis jemand `d.problems` rendert. |
| G9 | `goals-ui.js` Verlauf | Lädt `operate/overview` → `history`, nicht ein Goal-spezifisches Log. |
| G10 | Brainstorm „Vorschläge holen“ | Klingt nach KI; `project_route_support.py` ist heuristisch. Placeholder-Copy ist ehrlich, der Button nicht. |
| G11 | `workspace_mutation_routes.py` | Request-Feld `success` default `True` — Feedback kann Erfolg vortäuschen. |

---

## 4. OK / verbessert — Regel wird bereits eingehalten

### Auf `master`

- **EIDO-007:** Chat-UI kein `'Antwort erhalten'`. `ok === false` und leere `response` → Fehlertext (`chat-ui.js`, `tests/test_web_ui_contracts.py`).
- **EIDO-002 Kern:** `/healing/status` liest `SelfHealingService`, nicht mehr hart `{"status":"ok"}`. `/health.self_healing.available` folgt `running`.
- **EIDO-003 QUIC-Listener:** `/health.quic_port` ist `listening: false` / `not_wired`, wenn der Python-Listener nicht läuft. Vertragstest vorhanden. (Capability `mesh.quic` driftet trotzdem, siehe K2.)
- **Chat-Operate-Tür (UI):** Freigeben/Ablehnen nur bei pending Gates; „Weiter“ nur bei `next_step` ohne Approvals. Formation „Ja, übernehmen“ / „Nein, nur im Chat“ gegen `POST /workspaces/formation`.
- **Projektboard:** Rename/Status/Gruppe/Reihenfolge gegen Projekt-APIs. Brainstorm kommt aus dem Kernel, nicht aus einem Domänen-Paket; Copy sagt das.
- **Backups:** Create/Restore/Delete mit Scharfstellen, echte Endpunkte.
- **Pairing:** Self-Pairing-Block und Browser-Geräteidentität aus EIDO-021 sind im Codepfad; Mesh-Liste mischt Peers + Paired ohne Demo-Peer.
- **Code-Reparatur-UI:** `proposal_only` / `applied: false` → Warnung, nicht „Fix angewendet“.
- **Identität:** `/identity` trennt aktive Rollen und Vorlagen.
- **Arbeitsspur:** `data-work-trace` aus Kernel/Session, ohne Fake-Aktivität.

### PR #11 (`cursor/llm-provider-registry-8680`) — LLM/Settings

Das ist der größte Honesty-Schnitt seit EIDO-021, **noch nicht auf master**:

- Ein Provider-Register: Ollama, OpenAI-kompatibel (Key + `base_url`), ChatGPT-Login nur über Codex.
- UI fälscht OAuth nicht für Key-Only-Provider; ohne Codex-CLI: „es gibt keinen Fake-Login“.
- Ersatzkette sortierbar, persistiert; leer/ungültig wird **abgelehnt**, nicht still repariert.
- Chat wendet Settings nur bei ausdrücklichem Wunsch an; Secrets nie zurück.
- `/llm/connection` und Chat-Kontext zeigen Probleme ohne Schlüsselwerte.
- `testOpenAIChat` liest `result.reply || result.response` (auf master nur `reply` → leerer Success-Toast).

**Offen in #11:** K2–K6, M1–M3, M7–M10 bleiben. Healing/Self-Repair bewusst als Follow-up markiert — das ist ehrlich, solange die UI nicht „repariert“ behauptet.

---

## Bekannter Kontext — verifiziert

| Claim | Stand 2026-09-05 |
|---|---|
| EIDO-007 Chat Fake-Success | **Behoben** auf master (Frontend). Serverseitiges unmarkiertes Fallback bleibt M4. |
| EIDO-021 OAuth-Honesty | **Teilweise / Drift.** Route `/llm/openai/api-key` ist auf master **weg**; Totcode `saveOpenAIKey()` bleibt. Header behauptet API-Key + „OAuth nicht implementiert“, Dropdown bietet Login (K1). PR #11 räumt die LLM-Fläche weitgehend auf. |
| Freigabe nur „Weiter“ | **Erklärbar und real.** Tür existiert für Keyword-Buchung/Extern nach Formation-Confirm. Sonst nur Phasen-„Weiter“. Freigeben führt die Folgeaktion nicht aus (K4). |
| SelfHealingService existiert | **Verdrahtet und gestartet.** Status ehrlich bzgl. running/stopped. Checks/Recovery überzeichnen (M2). Kein Self-Repair-OS. |

---

## Priorisierte Fix-Reihenfolge (nur Richtung)

1. **K6** Self-Reflection-Envelope — höchste Chat-Sichtbarkeit: Erfolg wird als Fehler gezeigt.
2. **K1** Settings-Login-Toasts und `/integrations/openai/*` `ok`-Semantik. PR #11 senkt das Risiko, ersetzt aber nicht den Auth-Endpunkt auf master. Statischen Header an Codex-Login angleichen; API-Key-Totcode entfernen.
3. **K2** Capability-Checks entlügen (vor allem `llm.ollama`, `autonomy.loop`, `skills.runtime`, Default-`True`).
4. **K4** Freigabe-Copy / fehlender Executor; Chat-Fallback wie Operate; „Weiter“ nicht als Ausführung lesen.
5. **K3 / K5** Skills- und Health-Flächen auf echte Quellen oder `unavailable`.
6. **M1 / M8** Settings nur speichern, was wirkt — oder Wirkung kennzeichnen.
7. **M2 / M9 / M10** Healing-Toasts, Kontext-Capabilities, Operate-Fehlerfeedback.

Keine Merge-Empfehlung für diesen Audit-PR. PR #11 nicht mergen, solange K2–K6 und M8 ungeprüft bleiben; LLM-Honesty dort ist trotzdem ein Fortschritt gegenüber master.
