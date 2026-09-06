# Eidolon Evolution Stage

> Status: verbindlicher Produktvertrag für **Parität**, **nächste Stufe**, **Instinkt-UX** und **Ehrlichkeit**.
> Dieses Dokument beschreibt **Soll** plus den **heute belegbaren Ist-Abstand**.
> Es behauptet **nicht**, Eidolon sei Feature-für-Feature OpenClaw, Hermes oder Grok Bot.
> Es behauptet **nicht**, dass „keine Fehler“ metaphysisch erreichbar sei.

## Zweck

Muhammets Brief: Eidolon muss die nächste Evolution von AI-Agenten sein — alles, was ein Messenger-Agent können muss, plus die Stufe danach; anti-placebo; instinktiv benutzbar.

Die bestehende Spezifikation (`eidolon-specification.md`, `eidolon-product-identity.md`) definiert ein agentisches Hauptsystem, mappt aber **nicht** explizit gegen OpenClaw / Hermes / Grok Bot und benennt **nicht** die nächsten Stufen als Vertrag.

Diese Lücke schließt **dieses** Dokument. Es ist Produktvertrag, keine Marketingfolie.

## Leseregel

Statuswerte in den Checklisten:

| Token | Bedeutung |
|---|---|
| `required for parity` | Ohne diese Fähigkeit ist Eidolon kein vollwertiger Agent gegenüber Messenger-Agenten. |
| `already in Eidolon` | Im **live Python-Produkt** verdrahtet und über Datei/Route/Test belegbar. |
| `gap` | Im live Produkt **nicht** als diese Fähigkeit vorhanden. Nicht als `echt` framen. |

Zusatzregeln:

- Belege kommen nur aus **diesem Repo** (live `python/`, `tests/`, aktive Docs). Nicht aus `SPECS/`, `sketches/`, `.hermes/plans/`, quarantiniertem Rust oder `docs/eidolon-competitor-comparison.md`.
- Die Vergleichsmatrix `docs/eidolon-competitor-comparison.md` ist eine **externe** Notiz. Sie darf diesen Vertrag nicht als Ist überschreiben. Mehrere dort genannte Eidolon-Fähigkeiten (volles Tool-Ökosystem, Consumer-Multi-Channel, fertiges Skill-Lernen) sind hier `gap`.
- Teilweise vorhandene Bausteine machen eine Paritätsfähigkeit **nicht** zu `already in Eidolon`. Was fehlt, bleibt `gap`; vorhandene Bruchstücke stehen in der Spalte *Was real da ist*.

---

## 1. Basisfähigkeiten (Parity)

Was ein Messenger-Agent (OpenClaw, Hermes, Grok Bot) können muss und Eidolon **nicht verlieren** darf. Das ist die Untergrenze, nicht die Differenz.

### 1.1 Chat-Kanal

| | |
|---|---|
| **Status** | `required for parity` · `already in Eidolon` |
| **Soll** | Ein dauerhafter Gesprächskanal: Nachricht senden, Antwort lesen, Session fortsetzen. |
| **Ist** | Lokaler Web-Chat ist die Starttür (`/#chat`). `POST /chat` und `GET /chat/context` teilen denselben `session_payload`-Pfad. `stream: true` liefert SSE; echte Tokens nur vom OpenAI-kompatiblen (Groq) Pfad, sonst ein `done` ohne Fake-Typewriter. Sessions liegen in `ChatSessionStore` (`state/user/chat_sessions.json`). Mobile Pairing landet in derselben App-Shell `/#chat`. |
| **Beleg** | `python/eidolon/chat_message_routes.py`, `python/eidolon/chat_session_routes.py`, `python/eidolon/server_chat_sessions.py`, `python/eidolon/web/chat-ui.js`, `ARCHITECTURE.md` |
| **Nicht behauptet** | Kein Telegram-, WhatsApp-, Slack-, Discord- oder Signal-Kanal. Das ist 1.2. |

### 1.2 Multi-Channel / Messenger-Gateway

| | |
|---|---|
| **Status** | `required for parity` · `gap` |
| **Soll** | Dieselbe Arbeitswahrheit über mehrere Kanäle (Messenger, CLI, Web), nicht nur ein Browser-Tab. |
| **Ist** | Keine Channel-Adapter für Telegram/WhatsApp/Slack/Discord/Signal/iMessage im live Python. `GET /ws` ist ein Echo-Socket, kein Event-Bus. |
| **Was real da ist** | Web-UI, gekoppeltes Mobile in derselben Shell, Rust-CLI als HTTP-Client gegen FastAPI (`crates/eidolon-cli`). |
| **Beleg für das Gap** | Keine Treffer für Telegram/WhatsApp/Discord/Slack als Produktkanal unter `python/eidolon/`. `python/eidolon/system_status_routes.py` (`/ws` echo). |

### 1.3 Tools / Skills als Agent-Handlung

| | |
|---|---|
| **Status** | `required for parity` · `already in Eidolon` (kleine ehrliche Runtime) |
| **Soll** | Der Agent ruft im Turn echte Tools/Skills auf (lesen, schreiben, ausführen, recherchieren) und berichtet das Ergebnis. |
| **Ist** | `POST /chat` erkennt konservativ Skill-Absicht. Live-Skills `note`, `system_info`, `device_status` rufen echte `run()`-Handler auf und liefern Host-/Store-Daten. Katalog-Skills (`calendar`, `file_organizer`, `mesh_send`, `goal_manager`, …) antworten ehrlich „nicht verdrahtet“ — kein Fake-Erfolg. `arbeitet` wird nur gesetzt, während ein Live-Skill läuft. Mehr bleibt ein Katalog; verdrahtete Zeilen sind als ausführbar im Chat markiert. |
| **Was real da ist** | `python/eidolon/skills/live_skills.py`, `python/eidolon/skills/chat_skill_turn.py`, `python/eidolon/chat_message_routes.py`. Datei-Handler: `note.py` → `notes.json`, `system-info.py` → Host/psutil, `device-status.py` → Mesh-Store. |
| **Nicht behauptet** | Kein OpenClaw/Hermes-Tool-Ökosystem, kein MCP, kein Skill-Import, kein Kalender-Backend, kein Datei-Umordnen aus dem Chat, kein Mesh-Versand aus dem Gespräch. |

### 1.4 Memory — nur wo real

| | |
|---|---|
| **Status** | `required for parity` · siehe Zeilen darunter |

**Session- und Arbeitsgedächtnis** — `already in Eidolon`

- Chat-Sessions persistieren Nachrichten serverseitig.
- Operate speichert `WorkSessionRecord` / `ObjectiveRecord` / `AgentRunRecord` in SQLite.
- `topic_attention_store.record_interaction` schreibt Gesprächssignale.
- Beleg: `server_chat_sessions.py`, `operate/store_*.py`, `chat_message_routes.py`.

**Hermes-artige Langzeitgedächtnis / Skill-Selbstverbesserung** — `gap`

- Kein FTS5-Cross-Session-Recall, kein User-Modeling, keine geschlossene Skill-Lernschleife im live Chat.
- `skill-generator.py` liest `state/persistence/chat_history.json`; der live Store ist `state/user/chat_sessions.json`. Der Generator ist damit vom Produktchat entkoppelt.
- `KnowledgeGraph` in `/health` wird mit `available: True` und harten Null-Stats gemeldet (`runtime_health_payloads.py`) — das ist **kein** belastbares Memory-Produkt.
- Orchestration-Memory speichert Modul-Konfidenz, kein Gesprächsgedächtnis.

**Ehrliche Grenze:** Memory darf nur dort als vorhanden gelten, wo ein Store gelesen **und** geschrieben wird und die UI/API denselben Store nutzt. LocalStorage `eidolon-chat-messages` ist UI-Cache, nicht Kernel-Wahrheit.

### 1.5 Steuerfläche (Slash / Commands oder ehrliches Äquivalent)

| | |
|---|---|
| **Status** | `required for parity` · `already in Eidolon` (Äquivalent) |
| **Soll** | Der Nutzer steuert den Agenten explizit: fortsetzen, freigeben, ablehnen, Status, Geräte, Settings. Entweder Slash-Grammatik **oder** eine gleich ehrliche Fläche. |
| **Ist** | Keine Slash-Parser-Grammatik im Chat (`/`-Commands sind `gap`, werden nicht behauptet). Das Äquivalent ist verdrahtet: Chat-Buttons Freigeben / Ablehnen / Weiter gegen Operate-APIs; Formation Bestätigen/Ablehnen gegen `POST /workspaces/formation`; Rust-CLI (`pair`, `projects`, `goals`, `settings`, `api`); Settings-Intent im Chat (`parse_settings_intent` → `apply_user_settings`). |
| **Beleg** | `python/eidolon/web/chat-ui.js`, `python/eidolon/web/operate-render-ui.js`, `crates/eidolon-cli/src/main.rs`, `python/eidolon/core/settings_intent.py` |

### 1.6 Status / Presence

| | |
|---|---|
| **Status** | `required for parity` · `already in Eidolon` (Kernel + Chat-Phasen) |
| **Soll** | Sichtbar, ob der Agent bereit ist, denkt, arbeitet, wartet, blockiert oder fertig ist — aus echtem Zustand, nicht aus Dekor. |
| **Ist** | Signature-Object und Presence (`idle` / `thinking` / `acting` / `waiting` / `blocked` / `done`) aus Operate (`describeOperatePresence` → `setEidolonPresence`). Chat-Turn-Status `denkt` / `arbeitet` / `antwortet` über `GET /chat/turn-status`. `POST /chat` setzt `denkt` und `antwortet`; während echter Stream-Deltas bleibt die Phase `antwortet`. Die eine Live-Chat-Marke (`#chat-eidolon-presence`) sitzt im Composer-Chrome **über dem Eingabefeld**, neben dem Phasen-Text (`denkt…`). Keine Avatare an Du-/Eidolon-Zeilen. Das Transcript (`.chat-messages`) scrollt in einer begrenzten Kartenhöhe; Composer + Presence bleiben unten fixiert. Die Sidebar-Signature bleibt sekundär. Innere Bewegung kommt aus `eidolon-presence.js`: WebGL-Curl-/Domain-Warp der Still-Texel (Canvas-2D-Gitter-Warp als Fallback) plus ein Gold-Mote. Drei lesbare Signaturen: `schreibt` (Composer-Fokus/`#chat-input`, langsamer Horizontal-Drift, weiches Glow, `data-presence-phase="schreibt"`, Aria „Eidolon achtet auf die Eingabe“; `data-turn-phase` bleibt `idle`), `denkt` (schneller Filament-Churn, helles Mote, ehrliche Turn-Phase), `antwortet` (sprechender Puls, Gaze nach links/oben zum Transcript). Idle ohne Fokus ist leiser, aber lebendig. Die Textur lädt immer den PNG-Pfad (`img[src]`), nie das `<picture>`-WebP, damit Safari/iOS WebGL nicht auf einer WebP-Quelle scheitert; schlägt WebGL fehl, bleibt Canvas2D sichtbar lebendig. `data-presence-engine` meldet `webgl` / `canvas2d` / `still`. `/assets/eidolon-presence.js` ist per Query-Version und `Cache-Control: no-cache` cache-bust. Turn-Phasen kommen nur aus `data-turn-phase` (`setEidolonTurnPhase`); die sichtbare Motion-Phase steht in `data-presence-phase` plus `is-schreibt` / `is-denkt` / `is-antwortet`. `prefers-reduced-motion` und Settings `ui.animations=off` zeigen nur das genehmigte Still; unsichtbare Marks pausieren. Healing-/LLM-Probleme erscheinen in Connection/Systemstatus, nicht als Fake-Erfolg. |
| **Gap innerhalb der Phase** | `arbeitet` setzt der normale `/chat`-Pfad nur, während ein Live-Skill wirklich läuft. Die UI faked diese Phase nicht. Keine Emotions-, Stimmen- oder Tool-Work-Visuals. Kein CSS-Pan/Zoom des Still-Bitmaps als Haupteffekt. Presence bleibt eine Marke (42px Composer, max. 48px Chat / 56px Sidebar), kein Idle-Hero und kein Zeilen-Avatar. |
| **Beleg** | `python/eidolon/chat_turn_status.py`, `python/eidolon/chat_message_routes.py`, `python/eidolon/operate_api_self_reflection_chat.py`, `python/eidolon/web/app-shell.js`, `python/eidolon/web/chat-ui.js`, `python/eidolon/web/eidolon-presence.js`, `python/eidolon/web/components/shell/eidolon-presence.css`, `tests/test_presence_avatar_contracts.py` |

### 1.7 Always-on-Erreichbarkeit

| | |
|---|---|
| **Status** | `required for parity` · lokal `already in Eidolon` · Messenger/Cloud `gap` |
| **Soll** | Der Agent ist ansprechbar, ohne jedes Mal eine neue App-Session zu erfinden. OpenClaw/Hermes lösen das über ein Gateway plus Kanäle. |
| **Ist** | Solange der Python-FastAPI-Prozess läuft, sind Chat, Operate, Pairing und CLI gegen denselben Server erreichbar. `eidolon-core` hat `instantiation_policy=always_on`. Mesh-Pairing koppelt Geräte an diese Runtime. |
| **Gap** | Kein gehosteter 24/7-Bot, kein Push in Messenger, kein Hintergrund-Daemon unabhängig vom lokalen Server. `/ws` trägt keinen Produktzustand. |
| **Beleg** | `ARCHITECTURE.md` (einzige live Runtime), `python/eidolon/bots/role_catalog.py`, `python/eidolon/mesh_pairing_routes.py` |

### 1.8 Kurzmatrix

| Fähigkeit | Pflicht | Stand | Eine Zeile Ist |
|---|---|---|---|
| Chat-Kanal (Web/Mobile lokal) | `required for parity` | `already in Eidolon` | `/#chat`, `POST /chat`, Sessions, Pairing in dieselbe Shell |
| Multi-Channel Messenger | `required for parity` | `gap` | keine Channel-Adapter |
| Tools/Skills im Agent-Turn | `required for parity` | `already in Eidolon` | Kleine Chat-Runtime: note, system_info, device_status; Rest ehrlich unwired |
| Session-/Arbeitsgedächtnis | `required for parity` | `already in Eidolon` | Chat-Sessions + Operate-SQLite + Topic-Signale |
| Semantisches Langzeitgedächtnis | `required for parity` | `gap` | kein Cross-Session-Recall, Generator entkoppelt |
| Steuerfläche (kein Slash nötig) | `required for parity` | `already in Eidolon` | Freigabe/Weiter/Formation/CLI/Settings-Intent |
| Slash-Grammatik | optional, wenn Äquivalent ehrlich | `gap` | nicht vorhanden, nicht behaupten |
| Status/Presence | `required for parity` | `already in Eidolon` | Signature + Turn-Status; innere Tintenbewegung + Mote an echte Phasen; `arbeitet` nur wenn gemeldet |
| Always-on lokal | `required for parity` | `already in Eidolon` | FastAPI-Prozess + Pairing |
| Always-on Messenger/Cloud | `required for parity` | `gap` | kein Gateway-Kanal |

---

## 2. Nächste Stufe (Eidolon-Differenz)

Was über einen Messenger-Agenten hinausgeht. Das ist der eigentliche Produktkern. Jede Zeile ist konkret und mit Ist-Abstand.

### 2.1 Operate-Kernel als Wahrheit

**Soll:** Session, Ziel, Lauf, Subagent, Freigabe, Blocker, Evidence und nächster Schritt sind **ein** persistiertes Modell. UI darf verdichten, nicht eine zweite Wahrheit erfinden.

**Ist (`already in Eidolon` als Kernel, nicht als vollständige Einheitsfläche):**

- Records und SQLite-Store existieren: `WorkSessionRecord`, `ObjectiveRecord`, `AgentRunRecord`, `SubAgentRunRecord`, `ApprovalGateRecord`, `BlockingIssueRecord`, `EvidenceItemRecord`, `TransitionEventRecord`, `NextActionRecord`.
- Produktphasen sind als Vertrag gemappt (`product_phases.py`).
- Chat, Arbeit und Projektfläche **lesen** denselben Operate-/`work_kernel`-Snapshot.

**Offen (`gap` zur vollen Differenz):**

- Board-Element-Blocker und `BlockingIssueRecord` sind noch zwei persistierte Modelle (`ROADMAP.md`).
- Chat-Landing holt den Operate-Tür-Snapshot über `GET /chat/context` (`operate_overview` + `runtime_context.operate_context`). Arbeit bleibt auf `/api/v1/operate/overview`.
- Chat-UI hält zusätzlich `localStorage` (`eidolon-chat-messages`) — Cache, nicht Kernel.

**Beleg:** `python/eidolon/operate/contract_*.py`, `python/eidolon/workspaces/work_truth.py`, `ROADMAP.md`.

### 2.2 Chat → Projekt → Board → Freigabe

**Soll:** Aus einem Vorhaben wird kein stilles Projekt. Der Weg ist sichtbar: Gespräch → Kandidat → bestätigtes Projekt → Board-Karten → Freigabe nur wo konsequential.

**Ist (`already in Eidolon` als Vertrag):**

- `POST /workspaces/formation`: `chat_topic` → `project_candidate` sichtbar; `project_candidate` → `active_project` nur mit `confirmed=true`.
- Arbeitsorientierte Nachrichten erzeugen den Kandidaten deterministisch (ohne LLM).
- Bestätigung legt das Projekt an und seedet textgebundene Board-Karten (idempotent).
- Buchung / externe Schreibaktion öffnet eine echte `ApprovalGateRecord`. Weiter ist Fortsetzen, nicht heimliche Freigabe.

**Beleg:** `docs/project-formation-rules.md`, `python/eidolon/workspaces/project_formation.py`, `tests/test_chat_stewardship_contracts.py` (Tür bleibt schlank; Handlungen bleiben echt).

### 2.3 Sichtbare Arbeit

**Soll:** Nutzer sieht jederzeit Kontext, Ziel, Zustand, Zuständigkeit, offenen Blocker, offene Freigabe, nächsten Schritt. Autonomie ohne diese Sichtbarkeit ist verboten.

**Ist (`already in Eidolon` auf Arbeit/Operate; Chat verdichtet):**

- Operate-UI zeigt Lauf, Freigaben, Blocker, Evidence, Next Action.
- Chat zeigt Formation und Operate-Handlungen, wenn sie real anliegen — auch auf der Idle-Tür, sobald eine Freigabe, ein Blocker oder ein fortschreibbarer nächster Schritt im Kernel offen ist. Kein Idle-Freigabe-Wand ohne Anlass.
- Idle-Chat ist Titel + Composer, optional eine Projektzeile (`Titel · öffnen`).

**Beleg:** `python/eidolon/web/operate-render-ui.js`, `python/eidolon/web/chat-ui.js`, `docs/eidolon-ui-workspace-architecture.md`, `tests/test_chat_stewardship_contracts.py`.

### 2.4 Rollen-Bots unter einem Hauptsystem

**Soll:** Spezialisten entstehen als organisatorische Rollen **unter** Eidolon. Keine Persona-Zoo, keine entkoppelten Bots. Dauerhafte Rollen nur mit Erklärung und Freigabe.

**Ist:**

- `already in Eidolon`: Rollenregister, `eidolon-core` aktiv und löschgeschützt, Vorlagen `defined` (Projekt/Task/Meta), Freigabepflicht für Aktivierung, `/identity` und `/bots/roles`.
- `already in Eidolon` als Kernel-Vokabular: `SubAgentRun` mit `planner` / `research` / `builder` / `verifier` / … — Records, keine zweiten Chat-Gegenüber.
- `gap`: Es gibt **kein** zweites Gesprächsgegenüber im Chat. Die UI spricht mit „Eidolon“. Live gespawnte Projekt-Bots als eigene Sessions existieren nicht.

**Beleg:** `python/eidolon/bots/role_catalog.py`, `python/eidolon/bots/role_registry_ops.py`, `docs/bot-organization-model.md`.

### 2.5 Anti-Placebo

**Soll:** Keine Scheinerfolge, keine Demo-Daten als Wahrheit, keine toten Buttons, keine erfundenen Läufe. Unfähigkeit wird als Unfähigkeit gezeigt.

**Ist (`already in Eidolon` als Disziplin, nicht als magische Vollständigkeit):**

- Chat ohne Modellantwort zeigt Fehler, nicht „Antwort erhalten“ (`EIDO-007`).
- Capabilities kommen aus Checks, nicht aus Wunschlisten.
- Settings/Secrets erscheinen nicht in Antworten; leere Fallback-Ketten werden abgelehnt.
- Motion bestätigt nur reale Mutationen; Presence atmet aus Kernel/Session.
- Bekannte Uneinheitlichkeiten bleiben in Roadmap/Findings sichtbar statt „fertig“ zu lügen.

**Beleg:** `docs/findings/EIDO-007-chat-fake-success-fallback.md`, `python/eidolon/web/chat-ui.js`, `python/eidolon/core/capability_catalog.py`, `AGENT.md`.

### 2.6 Mehrere Clients, derselbe Zustand

**Soll:** Web, Mobile, CLI sehen dieselbe Session, dasselbe Projekt, dieselbe Freigabe.

**Ist:**

- `already in Eidolon` als Server-Wahrheit: alle Clients sprechen FastAPI; Operate/Projekte/Pairing liegen im externen State-Root.
- `gap` zur vollen Differenz: Chat-Transcript zusätzlich in `localStorage`; Board-Blocker vs. Operate-Blocker.

**Beleg:** `README.md`, `ROADMAP.md` (offene P0-Uneinheitlichkeiten), `python/eidolon/web/chat-ui.js` (`persistChatMessages`).

### 2.7 Instinktive UI + animierte Präsenz

**Soll:** Die Oberfläche erklärt sich selbst. Präsenz (Gaze/Status) ist an echte Phasen gebunden. Skizzen sind keine Produktwahrheit.

**Ist:**

- `already in Eidolon`: dunkle Schale, Chat-Tür statt Dashboard, genehmigtes Presence-Still als Marke über dem Composer und in der Sidebar-Signature, innere Tintenbewegung (WebGL-Warp, 2D-Fallback; PNG-Textur, nicht Picture-WebP) plus drei lesbare Motion-Signaturen: `schreibt` (Composer-Fokus/`#chat-input`), `denkt` und `antwortet`, Idle leiser, Chat-Status `denkt…` / `antwortet` am Turn, Action-Motion nur nach Mutation, `prefers-reduced-motion` + Settings `ui.animations` → statisches Still, `data-presence-engine` und `data-presence-phase` ehrlich.
- `already in Eidolon` für `arbeitet` im normalen Chat-Turn, aber nur während eines Live-Skills. Kein zweites Maskottchen-Zoo, kein Hero auf der Idle-Tür. Embodied Gaze in Skizzen bleibt Skizze; im Produkt gibt es nur den phasengebundenen Mote-Blick (Composer/Transcript), keine Emotionserkennung.

---

## 3. Instinkt-UX-Vertrag

Verbindlich für jede neue Oberfläche. Widerspricht eine Fläche diesem Vertrag, gilt die Fläche als Drift — auch wenn sie „mehr Features“ zeigt.

### 3.1 Fünf Eigenschaften

1. **Selbsterklärend** — Ohne Tutorial ist klar: worüber sprechen wir, was läuft, was braucht mich, was als Nächstes. Keine Semantik nur in Hover oder nur in Farbe.
2. **Unkompliziert** — Eine primäre Handlung pro Moment. Keine zweite Startwand, keine Utility-Flut auf der Tür.
3. **Übersichtlich** — Wenige sichtbare Dinge, Rest auffindbar. Idle bleibt leer und ehrlich.
4. **Animiert** — Bewegung bestätigt echte Phasen oder echte Mutationen. Kein Dekor-Loop, der Arbeit vortäuscht.
5. **Optisch ansprechend** — Dunkle Schale, Wärme aus Typo/Abstand/Akzent. Kein erzwungenes Light-Theme, kein Maskottchen, das den Kernel ersetzt.

### 3.2 Chat ist die Tür, nicht das Dashboard

- Default ist `/#chat`.
- Idle: Sessiontitel + Composer. Höchstens eine echte Projektzeile (`Titel · öffnen`).
- Keine Landing-Wand aus „Gerade aktiv“, Diagnosen, Hero-Signature oder Operate-Überblick.
- Freigaben, Blocker und nächster Schritt leben in **Arbeit**; im Chat nur als echte Handlung, wenn sie anliegen.
- Operate bleibt `#operate`, nie Default.

Beleg des heutigen Schnitts: `docs/eidolon-ui-workspace-architecture.md`, `tests/test_chat_stewardship_contracts.py`.

### 3.3 Kurze Mitspieler-Stimme

Bei Arbeit:

- höchstens 3–5 kurze Zeilen
- höchstens eine nächste Aktion **oder** eine Klärungsfrage
- kein Schema aus Intention / Richtungen / Empfehlung
- eine konkrete Board-Anbietung statt Essay („lege ich als Karte an“)
- keinen Projektzustand erfinden

Bei Smalltalk: normaler Gesprächspartner, nicht automatisch in Projektarbeit schieben.

Beleg: `python/eidolon/chat_runtime_prompting.py`, `python/eidolon/chat_quality_finalize.py`, `tests/test_chat_stewardship_contracts.py`.

### 3.4 Animierter Avatar nur verdrahtet

Erlaubte Chat-Phasen: `denkt` · `arbeitet` · `antwortet`.

Regeln:

- UI darf eine Phase nur zeigen, wenn Server oder lokaler Sendepfad sie **gesetzt** hat.
- `GET /chat/turn-status` ist die Serverquelle; der Client pollt nur während eines echten Sends.
- `arbeitet` darf nicht dekorativ zwischen `denkt` und `antwortet` geblinkt werden. `/chat` setzt sie nur, während ein Live-Skill wirklich läuft.
- Signature-Presence folgt Operate, nicht einem Zufallsgenerator.
- Der Chat-Avatar sitzt als Composer-Chrome **über dem Eingabefeld** (`#chat-eidolon-presence` in `.chat-composer-chrome`). Keine Avatare an Transcript-Zeilen. Das Transcript scrollt in `.chat-messages` bei begrenzter Kartenhöhe; Presence + Composer bleiben unten. Die Sidebar-Signature bleibt sekundär. Phasen-Text (`denkt…`) steht neben der Marke.
- Idle-Motion (innerer Tintenfluss + Lichtpuls + Mote-Drift) ist ruhige, aber bei 42–48px in 1–2s lesbare Präsenz, kein Arbeitsclaim.
- `antwortet` darf das Licht-Mote Richtung Transcript führen; `denkt`/`arbeitet` Richtung Composer. Das ist Phasen-Gaze, keine Emotions- oder Stimm-Erkennung.
- Innere Bewegung muss die Still-Texel versetzen (Warp/Partikel/Loop), nicht das Bitmap als Ganzes per `translate`/`scale`/`rotate` schieben.
- Die Live-Textur kommt vom PNG-`src`, nicht vom `<picture>`-WebP (Safari/iOS). WebGL-Fehler fallen auf einen lebendigen Canvas2D-Warp, nicht auf ein stilles Bitmap.
- `data-presence-engine` ist `webgl`, `canvas2d` oder `still` — Debug-Ehrlichkeit, kein Marketing.
- `prefers-reduced-motion` und `ui.animations=off` zeigen nur das genehmigte Still.
- Embodiment-Skizzen unter `sketches/2026-08-30_*` bleiben Skizzen.

---

## 4. Ehrlichkeit — was „keine Fehler“ heißt

„Keine Fehler“ / „zero bugs forever“ ist **kein** gültiges Soll. Software bleibt fehlerfähig. Das gültige Soll ist:

1. **Kein Fake-Erfolg.** Eine Aktion, die nicht gelaufen ist, darf nicht als gelaufen erscheinen. Leere Modellantworten, fehlende Backends, fehlende Skills und fehlende Kanäle werden als Fehler, `unavailable` oder `gap` gezeigt.
2. **Tests vor Merge.** Produktverträge (`pytest`, UI-Contracts, Endpoint-Checks) laufen, bevor eine Fläche „fertig“ heißt. `AGENT.md` bleibt das Verifikationsprotokoll.
3. **Bekannte Fehler sichtbar.** Offene Uneinheitlichkeiten stehen in `ROADMAP.md`, Findings und in diesem Dokument als `gap`. Sie werden nicht durch Umbenennen geschlossen.
4. **Kontinuierliche Verifikation.** Jeder neue Pfad muss denselben Kernel sprechen oder ehrlich sagen, dass er es noch nicht tut.
5. **Placebo ist der eigentliche Produktfehler.** Ein hübscher Dummy ist schlimmer als ein sichtbares Loch.

Prüfsatz:

> Wenn wir es nicht im live Code zeigen können, ist es `gap`.
> Wenn wir es zeigen, aber der Nutzer einen Erfolg sieht, den der Kernel nicht hat, ist es Placebo — und damit ein Spec-Bruch.

---

## 5. Was dieser Vertrag bewusst nicht tut

- Keine Feature-für-Feature-Kopie von OpenClaw, Hermes oder Grok Bot.
- Keine Übernahme von `SPECS/` oder Rust-Crates als live Produkt.
- Keine Gaze-/Embodiment-Skizze als Ist. Der verdrahtete Mote-Blick bei `antwortet` (Transcript) und `denkt` (Composer) ist Phasen-Gaze, kein Embodiment-Theater.
- Kein Anspruch auf Multi-Channel, MCP, Skill-Import oder Video, solange der Code das nicht tut.
- Kein „wir sind schon die nächste Stufe in allen Flächen“ — Kernel und Formation sind real; Consumer-Reichweite und Tool-Loop sind `gap`.

## Verbindlicher Prüfsatz

Wenn eine spätere Entscheidung diesen Vertrag bricht, gilt in dieser Reihenfolge:

1. **Kein Placebo** vor Demo-Eindruck
2. **Operate-Wahrheit** vor zusätzlicher Fläche
3. **Chat-Tür** vor Dashboard
4. **Parität ehrlich halten**, bevor neue Kanäle beworben werden
5. **Bekannte Lücken sichtbar lassen**, statt sie zuzukleistern
