# ROADMAP — Eidolon Central Agentic System

> Status: konsolidierter aktueller Fortschritts- und Prioritätenstand.
> Diese Datei ist die Quellwahrheit für **heutigen Projektfortschritt**, nicht ein ungeprüftes Archiv aller früheren Phase-Claims.

## Bereits konsolidiert
- Produktidentität als **zentrales agentisches Hauptsystem** explizit gemacht
- Chat-Antwortvertrag auf knappe Mitspieler-Antworten gehärtet (kein Intention/Richtungen/Empfehlung-Essay)
- Rollenmodell trennt aktive Rollen von definierten Vorlagen
- Operate-Kernel mit Run-, Approval-, Blocker-, Evidence- und Next-Action-Verträgen vorhanden
- Workspace-Bridge speist Operate aus aktivem Projektkontext
- `workspace_ui_service.py`, `operate/bridge.py` und `operate/service.py` entlang echter Produktgrenzen zerlegt
- `runtime_bootstrap.py`, `work_context_kernel.py`, `goal_deriver.py`, `mesh_service.py`, `mesh_support.py` und `app-components.css` in kleinere Verantwortungsflächen aufgeteilt
- `role_registry.py`, `autonomy_runtime.py`, `server_support.py`, `operate_api_routes.py`, `project_model.py` und `chat_runtime.py` weiter in schmale Vertrags- und Runtime-Module zerlegt
- `semantic_clustering.py`, `topic_attention.py`, `cert_manager.py`, `backup_service.py`, `llm_backend.py`, `operate/contracts.py`, `operate/store_run_state.py` und `project_routes.py` weiter entlang echter Domänen- und Vertragsgrenzen zerlegt
- `autonomy_compat_routes.py`, `autonomy_goal_ops.py`, `workspace_routes.py`, `mesh/peers.py`, `module_runtime.py`, `skills/registry.py`, `proactive_assistance.py`, `settings_store.py`, `evidence.py` und `auth_manager.py` weiter entlang echter Verantwortungsgrenzen zerlegt
- `workspaces/state.py`, `workspace_actions.py`, `auth_store.py`, `orchestrator.py`, `chat_and_code_routes.py`, `voice_runtime.py`, `config.py`, `registry.py`, `ui/hud.py` und `runtime_health_routes.py` weiter entlang echter Runtime- und Produktgrenzen zerlegt
- `auth_models.py`, `role_registry.py`, `work_context_builder.py`, `store_foundation.py`, `mesh_handler.py`, `capabilities.py` und `workspace_support.py` in schmale Fassaden plus neue Hilfsmodule zerlegt
- `mesh_service.py`, `operate/contract_records.py`, `mesh/transport/quic_server.py`, `healing.py`, `server_backups.py`, `browser_control.py` und `settings_schema.py` weiter in schmale Fassaden plus Hilfsmodule zerlegt
- `chat_runtime_quality.py`, `autonomy_goal_mutations.py`, `project_analyzer.py`, `domain_engine.py`, `domain_models.py`, `workspace_service.py`, `operate/bridge.py` und `server_chat_sessions.py` weiter in schmale Fassaden plus Hilfsmodule zerlegt
- `workspace_payloads.py`, `bridge_workspace.py`, `service_support.py`, `runtime_support.py`, `runtime_service_factory.py`, `auth_logic.py`, `module_runtime_actions.py`, `mesh_pairing_routes.py`, `mesh/inbox.py`, `store_schema.py`, `settings_validation.py`, `semantic_clustering.py`, `topic_attention_analysis.py` und `memory/graph.py` erneut entlang echter Verantwortungsgrenzen mit kompatiblen Fassaden zerlegt
- Chat-POST `/chat` und Chat-GET `/chat/context` erzeugen ihren Runtime-Kontext jetzt über denselben `chat_route_support.session_payload`-Pfad auf Basis des `work_context_kernel`
- Goals-, Chat- und Shell-CSS werden über importierte Slice-Dateien statt über große Einzelfiles ausgeliefert
- Chat ist jetzt auch in der Web-UI die echte Startoberfläche; die Shell priorisiert Unterhaltung, aktive Arbeit und Projekte vor Utility-Flächen
- Operate-Panel ist wieder verdrahtet und über `#operate` erreichbar, ohne Default zu sein
- Projektfläche öffnet in der Planungsansicht (Zusammengehörig / Geplant / In Arbeit / Fertig / Archiv) mit Umbenennen, Status, Gruppe, Reihenfolge, Ablegen und Streichen gegen echte Projekt-APIs
- Projektstatus planned/in_progress/done/archived ist über `PUT /projects/{id}` editierbar
- Chat-Tür bleibt schlank (Titel + Composer, optional eine Projektzeile); Freigaben, Blocker und nächster Schritt leben in Arbeit und bleiben im Chat nur als echte Handlung erreichbar
- Chat, Arbeit und Projektfläche teilen denselben Operate-/Kernel-Snapshot für Freigaben, Blocker und Next Action; Projektmutationen schreiben nicht mehr in einen leeren parallelen `operate`-Pfad
- Projektbildung ist ein expliziter Vertrag (`POST /workspaces/formation`): `chat_topic` → `project_candidate` sichtbar, `project_candidate` → `active_project` nur mit Nutzerbestätigung
- Arbeitsorientierte Chat-Nachrichten erzeugen den Kandidaten deterministisch (ohne Ollama); Chat zeigt Bestätigen/Ablehnen
- Bestätigung legt das Projekt an und füllt das Board mit generischen Planungselementen aus dem Vorhaben
- Consequential next steps (Buchung / externe Aktion) erzeugen eine echte Operate-Freigabe; Chat und Arbeit zeigen dann Freigeben/Ablehnen, Weiter nur als Fortsetzen
- Generisches Karten-/Slot-Gerüst ohne Domänen-Pakete, Slots werden situationsabhängig aus Kernel/Workspace verdichtet
- Python FastAPI ist dokumentiert und durch Port-Wächter als einzige live Runtime gegenüber Rust abgegrenzt
- Ein kleines zustandsfähiges Eidolon-Signature-Object transportiert reale Arbeitszustände statt bloßes Dekor
- Idle-Projektfläche ist handlungsfähig: große Primäraktion „Neues Projekt“ plus leeres Board, ohne Operate-Überblickswand
- Schmale Projektfläche (≤768px, inkl. 390px) ist eine senkrechte Kartenwand mit Statuschip und Ideen-Zeile gegen `POST /projects/{id}/elements`; Desktop behält horizontale Spalten; „Bausteine ergänzen“ ist zu Kernel-Vorschlägen als Entwurfskarten zurückgestuft
- Idle-Arbeit zeigt drei klare Wege (Chat, Übernahme aus Projektfläche, Hinweis auf Freigaben) statt einer leeren Sektionswand
- Kurze Action-Motion bestätigt nur reale Mutationen und respektiert `prefers-reduced-motion` sowie Settings `animations`
- Idle-UI bleibt schlank (Chat: Titel + Composer, keine Landing-Wand); Dark-Theme ist wärmer, Arbeitsspur atmet in Arbeit/Projektfläche aus Kernel-/Sessiondaten ohne Fake-Läufe
- Findings- und Root-History-Dokumentation haben jetzt explizite Supersession-/Archiv-Readmes
- `/identity` liefert konsistente Produktrolle
- Runtime-State wurde aus dem Repo nach `%LOCALAPPDATA%/Eidolon/state/` ausgelagert
- `python -m pytest -q` → Formation-/Board-Karten-/Freigabe- und Altverträge; vorbestehende Env-Fehler (kein Live-Ollama, kein `aioquic`, Codex-CLI/`oauth_supported` false) bleiben außerhalb dieses Schnitts
- Bestätigtes Vorhaben füllt das Board mit unterscheidbaren, textgebundenen Karten (Fakten/Bedingungen in Notizen); erneutes Seed verdoppelt nicht
- LLM-Anbieter liegen in einer Registry: Ollama, OpenAI-kompatibel (`base_url` + Key + Modell, optionale Presets wie Groq) und Codex-OAuth; OAuth wird nur für den Codex-Pfad gezeigt; `complete()` folgt der Ersatzkette (gewählt zuerst, dann `fallback_chain`); Schlüssel erscheinen nicht in Settings-/Connection-/Chat-Antworten
- Ersatzkette ist in den Settings sortierbar und persistent; leer/ungültig wird ehrlich abgelehnt. Chat und Operate wenden Settings nur auf ausdrücklichen Wunsch an (`POST /settings/apply`, `POST /api/v1/operate/settings/apply`); Schema lehnt ungültige Werte ab, Secrets bleiben draußen. Erkannte `/health`-, LLM- und SelfHealing-Probleme erscheinen im Connection-Status, Systemstatus und Stabilität, nicht als Chat-Tür-Diagnose. Kein neues Self-Repair-OS in diesem Schnitt.

## Offene Prioritäten

### P0 — Einheitswahrheit durchziehen
- **Produktvertrag geschlossen (Doku):** `docs/eidolon-evolution-stage.md` mappt Parität vs OpenClaw/Hermes/Grok Bot, benennt die Eidolon-Differenz und reframed „keine Fehler“ als kontinuierliche Verifikation + kein Placebo. Das schließt die Spec-Lücke, nicht die Implementierungs-`gap`s in dem Dokument.
- große UI-/JS-Hotspots (`python/eidolon/web/index.html`, `python/eidolon/web/app-shell.js`) weiter in stabile Produktmodule schneiden
- aktive Doku weiter synchron halten, wenn neue Runtime- oder UI-Schnitte dazukommen
- verbleibende Mesh-/Core-Hotspots nur mit Live-Verifikation weiter reduzieren
- **offen:** Workspace-Board-Blocker und Operate-`BlockingIssueRecord` werden in denselben Slots gezeigt, sind aber noch zwei persistierte Modelle; vollständige Write-Vereinigung der Element-Blocker in den Operate-Store ist nicht Teil dieses Schnitts
- **offen:** Chat-Landing liest denselben Overview-Snapshot wie Arbeit, erzeugt ihn aber noch über `/api/v1/operate/overview` plus `/chat/context` statt eines einzigen HTTP-Calls

### P1 — Runtime und Oberfläche weiter verdichten
- `python/eidolon/core/mesh_service.py`, `python/eidolon/core/auth_entities.py`, `python/eidolon/user/topic_attention.py` und andere verbleibende Domänen-Hotspots weiter entlang echter Zustandsgrenzen zerlegen
- Operate-/Workspace-Direktmanipulation im UI weiter verdichten, ohne zweite Wahrheitsmodelle aufzubauen
- historische Nebenachsen nur noch als sauber markierte Referenz erhalten

### P1 — Agentisches Produktmodell vertiefen
- Chat-Operate-Tür um Interrupts und feinere Next-Action-Gründe weiter verdichten
- direkte Bearbeitung der Arbeitswahrheit weiter an denselben Operate-/Workspace-Schreibpfad binden
- **Folge-PR, nicht dieser Schnitt:** tiefere Self-Repair-Autonomie (Code-Reparatur-Loops, Recovery über den vorhandenen `SelfHealingService` hinaus). Secrets und destruktive Live-Eingriffe bleiben hinter der Freigabe-Tür.

## Verifizierungsbasis
- `python -m pytest -q`
- `/identity`
- `/chat/context`
- `/api/v1/operate/overview`

## Hinweis zu älteren Phase-Dokumenten
Frühere detaillierte Phase-Claims und Analysen bleiben als Historie im Repo, sind aber **nicht** automatisch aktueller Fortschrittsstand. Wenn sie von Live-Code/Testlage abweichen, gewinnt diese Roadmap nur dann, wenn sie in derselben Änderung mit frischer Evidenz aktualisiert wurde.
