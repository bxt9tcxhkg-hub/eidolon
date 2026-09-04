# ROADMAP — Eidolon Central Agentic System

> Status: konsolidierter aktueller Fortschritts- und Prioritätenstand.
> Diese Datei ist die Quellwahrheit für **heutigen Projektfortschritt**, nicht ein ungeprüftes Archiv aller früheren Phase-Claims.

## Bereits konsolidiert
- Produktidentität als **zentrales agentisches Hauptsystem** explizit gemacht
- Chat-Antwortvertrag auf arbeitsführende Erstreaktionen gehärtet
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
- Projektfläche öffnet in der Planungsansicht (Zusammengehörig / Geplant / In Arbeit / Fertig) mit Umbenennen, Status und Reihenfolge gegen echte APIs
- Generisches Karten-/Slot-Gerüst ohne Domänen-Pakete
- Python FastAPI ist dokumentiert und durch Port-Wächter als einzige live Runtime gegenüber Rust abgegrenzt
- Ein kleines zustandsfähiges Eidolon-Signature-Object transportiert reale Arbeitszustände statt bloßes Dekor
- Findings- und Root-History-Dokumentation haben jetzt explizite Supersession-/Archiv-Readmes
- `/identity` liefert konsistente Produktrolle
- Runtime-State wurde aus dem Repo nach `%LOCALAPPDATA%/Eidolon/state/` ausgelagert
- `python -m pytest -q` besteht

## Offene Prioritäten

### P0 — Einheitswahrheit durchziehen
- große UI-/JS-Hotspots (`python/eidolon/web/index.html`, `python/eidolon/web/app-shell.js`) weiter in stabile Produktmodule schneiden
- aktive Doku weiter synchron halten, wenn neue Runtime- oder UI-Schnitte dazukommen
- verbleibende Mesh-/Core-Hotspots nur mit Live-Verifikation weiter reduzieren

### P1 — Runtime und Oberfläche weiter verdichten
- `python/eidolon/core/mesh_service.py`, `python/eidolon/core/auth_entities.py`, `python/eidolon/user/topic_attention.py` und andere verbleibende Domänen-Hotspots weiter entlang echter Zustandsgrenzen zerlegen
- Operate-/Workspace-Direktmanipulation im UI weiter verdichten, ohne zweite Wahrheitsmodelle aufzubauen
- historische Nebenachsen nur noch als sauber markierte Referenz erhalten

### P1 — Agentisches Produktmodell vertiefen
- Chat nicht nur richtungsstark, sondern weiter als operativer Einstieg für Approvals, Interrupts und Next Actions ausbauen
- direkte Bearbeitung der Arbeitswahrheit weiter an Operate/Workspaces anbinden

## Verifizierungsbasis
- `python -m pytest -q`
- `/identity`
- `/chat/context`
- `/api/v1/operate/overview`

## Hinweis zu älteren Phase-Dokumenten
Frühere detaillierte Phase-Claims und Analysen bleiben als Historie im Repo, sind aber **nicht** automatisch aktueller Fortschrittsstand. Wenn sie von Live-Code/Testlage abweichen, gewinnt diese Roadmap nur dann, wenn sie in derselben Änderung mit frischer Evidenz aktualisiert wurde.
