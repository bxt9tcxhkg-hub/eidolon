# Vergleichsmatrix: Eidolon vs Grok Bot vs OpenClaw vs Hermes

> Erstellt: 2026-09-03
> Quellen: Offizielle Dokumentation, GitHub-READMEs, Live-APIs

---

## 1. Übersicht

| Dimension | **Eidolon** | **Grok Bot** | **OpenClaw** | **Hermes** |
|-----------|-------------|--------------|--------------|------------|
| **Produkttyp** | Zentrales agentisches Hauptsystem | KI-Chatbot mit API-Fokus | AI-Gateway-Assistent (Multi-Channel) | Autonomer AI-Agent mit Skill-Lernschleife |
| **Entwickler** | Eigenentwicklung | SpaceXAI (xAI) | OpenClaw Foundation (Peter Steinberger) | Nous Research |
| **Primäreinstieg** | Chat (immer) | API / Web / Mobile Apps | Gateway + Multi-Channel (Telegram, WhatsApp, Slack, Discord, Signal, iMessage, ...) | CLI / Telegram / Discord / Slack / WhatsApp / 20+ Plattformen |
| **Center of Gravity** | Einheitliches agentisches Kernel mit WorkSession, Objective, Run, SubAgents | Grok 4.6 Modell mit Tool Calling (Web, Code Execution, Image, Video, Voice) | Gateway als lokale Control Plane für Sessions, Tools, Events, Channels | Closed Learning Loop: Skills, Memory, Bot Mode, Subagenten |

---

## 2. Architektur-Vergleich

| Dimension | **Eidolon** | **Grok Bot** | **OpenClaw** | **Hermes** |
|-----------|-------------|--------------|--------------|------------|
| **Betriebsmodus** | Lokaler Python-Server (FastAPI) + optionaler Rust-Mesh | Cloud-API (api.x.ai) | Lokaler Node.js Gateway | Lokal/Remote (6 Backends: Docker, SSH, Daytona, Singularity, Modal, lokal) |
| **State-Modell** | WorkSession → Objective → AgentRun → SubAgentRun (kanonischer Kernel mit SQLite) | Stateless (API-Call-basiert) | Gateway-managed Sessions | Persistent Memory + Skills + Bot State |
| **Datenpersistenz** | SQLite (Operate-Kernel) + LocalStorage (Chat) + Rust-Mesh (mTLS) | Cloud (API-Key) | Lokale Konfiguration | FTS5 SQLite (Memory) + Skill Store + Context Files |
| **Subagent-Modell** | SubAgentRun mit kanonischem State (queued/running/completed) + function_type (planner/researcher/builder/verifier/resolver/operator/monitor/reconciler/executor) | Tool Calling (Function Calling, Web Search, Code Execution, Image Generation) | Tools + Skills + Plugins (ClawHub) | Subagenten (parallel) + Programmatic Tool Calling via execute_code |
| **Multi-Channel** | Web UI, Mobile UI (geplant) | Web, iOS, Android (über xAI Apps) | 20+ Channels (WhatsApp, Telegram, Slack, Discord, Signal, iMessage, Google Chat, Teams, ...) | 20+ Platforms (CLI, Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, SMS, DingTalk, WeCom, QQ Bot, ...) |

---

## 3. Agent-Fähigkeiten

| Dimension | **Eidolon** | **Grok Bot** | **OpenClaw** | **Hermes** |
|-----------|-------------|--------------|--------------|------------|
| **Run-State-Machine** | Ja: understanding → planning → spawning_work → acting → waiting → blocked → verifying → completed | Nein (API-Response-basiert) | Nein (Gateway-basiert) | Ja (Bot Mode mit States) |
| **Phase-Preservation** | Ja: 8 Produktphasen als kanonischer Vertrag (chat_entry → understand_and_structure → context_classification → project_formation → workspace_composition → responsibility_derivation → execution → verification_and_return) | Nein | Nein | Nein (implizit) |
| **Approval Gates** | Ja: ApprovalGateRecord mit Status pending/approved/rejected | Nein | Ja (Pairing-basiert für DM-Channels) | Ja (Command Approval) |
| **Blocking Issues** | Ja: BlockingIssueRecord mit Kategorie (approval/credential/dependency/runtime_error/external_system/validation) | Nein | Nein | Nein |
| **Evidence-System** | Ja: EvidenceItemRecord mit evidence_severity (info/warning/critical) + is_completion_grade | Nein | Nein | Nein |
| **Autonomie-Modus** | bounded_autonomous / autonomous / manual | Keine Unterscheidung | Konfigurierbar (Security Policy) | Konfigurierbar |

---

## 4. Tool- und Skill-System

| Dimension | **Eidolon** | **Grok Bot** | **OpenClaw** | **Hermes** |
|-----------|-------------|--------------|--------------|------------|
| **Tools** | File read/write, Python execute, Browser control, Image generate, TTS, Mesh QUIC | Function Calling, Web Search, Code Execution, Image Generation, Video Generation | Tools + Skills + Plugins (ClawHub), Plugin SDK | 60+ built-in tools, Tool Gateway, MCP |
| **Skill-System** | 8 eingebaute Skills (chat, runtime_facts, system_info, goal_manager, device_status, mesh_send, note, file_organizer) | Keine | Ja (Skills + ClawHub, Community-basiert) | Ja (automatische Skill-Erstellung, selbstverbessernd, kompatibel mit agentskills.io) |
| **Externe Erweiterung** | Plugin-System (geplant) | API-Integration (Responses API, Batch, WebSocket) | Plugin SDK, MCP, ClawHub | MCP Server, Skills Hub |

---

## 5. Lernen und Persistenz

| Dimension | **Eidolon** | **Grok Bot** | **OpenClaw** | **Hermes** |
|-----------|-------------|--------------|--------------|------------|
| **Memory** | Session-basiert (WorkSessionRecord) | Nein (stateless) | Session-basiert (Gateway) | Persistent Memory (FTS5), cross-session recall, LLM-Summarization |
| **Selbstverbesserung** | Nein (statisch) | Nein | Nein | Ja (Skill self-improvement, autonomous skill creation, nudges) |
| **User Modeling** | User Preferences (LocalStorage) | Nein | Nein | Honcho dialectic user modeling |
| **Cross-Session** | SQLite-Persistenz | Nein | Gateway-Session | Ja (FTS5 cross-session recall) |

---

## 6. Wahrheit und Anti-Placebo

| Dimension | **Eidolon** | **Grok Bot** | **OpenClaw** | **Hermes** |
|-----------|-------------|--------------|--------------|------------|
| **Anti-Placebo-Policy** | Harte Regeln: kein Fake, keine Placebos, keine halben Lösungen | Nicht dokumentiert | Security Guide, Sandboxing | Command Approval, Authorization |
| **Completion-Grade Evidence** | Ja: is_completion_grade Feld, Severity-basiert | Nein | Nein | Nein |
| **Interrupt-Klassifikation** | Ja: refine / conflict / supersede | Nein | Nein | Nein |
| **Truth-Audit** | Dokumentiert (eidolon-vs-new-target-truth-audit.md) | Nein | Nein | Nein |

---

## 7. Multi-Agent / Subagent-Pattern

| Dimension | **Eidolon** | **Grok Bot** | **OpenClaw** | **Hermes** |
|-----------|-------------|--------------|--------------|------------|
| **Subagent-Typen** | Planner, Researcher, Builder, Verifier, Resolver, Operator, Monitor, Reconciler, Executor | Keine | Nodes (Companion Apps) | Isolierte Subagenten (parallel) |
| **Subagent-Kommunikation** | State-basiert über SQLite | Nein | Gateway-Events | execute_code (collapsing multi-step) |
| **Specialist Vocabulary** | Ja (kontrollierte Familien) | Nein | Nein | Nein |

---

## 8. Stärken und Schwächen

| System | Stärken | Schwächen |
|--------|---------|-----------|
| **Eidolon** | Kanonischer Kernel, Phase-Preservation, Anti-Placebo, Evidence-System, Wartbar | Wenig Channels, kein automatisiertes Lernen, kein Consumer-UI |
| **Grok Bot** | Leistungsstarkes Modell (Grok 4.6), Multi-Modal (Text/Image/Video/Voice), API-ökonomisch | Kein lokaler Betrieb, kein State-Model, keine Subagenten, stateless |
| **OpenClaw** | Multi-Channel-König (20+), Gateway-Sicherheit, Plugin-Ökosystem (ClawHub) | Kein kanonischer Agent-State, kein automatisiertes Lernen, kein Evidence-System |
| **Hermes** | Beste Learning-Loop (Skills, Memory, User Modeling), 60+ Tools, 20+ Channels, MCP | Keine kanonische Phase-Preservation, kein Anti-Placebo-Audit, komplexe Einrichtung |

---

## 9. Fazit: Wo steht Eidolon?

### Eidolon hat, was die anderen nicht haben:
- **Kanonischer Agent-Kernel** mit WorkSession → Objective → Run → SubAgentRun
- **Phase-Preservation** als harter Vertrag (8 Produktphasen)
- **Evidence-System** mit Completion-Grade und Severity
- **Anti-Placebo-Policy** mit Truth-Audit
- **Interrupt-Klassifikation** (refine/conflict/supersede)

### Was die anderen haben, was Eidolon nicht hat:
- **Multi-Channel** (OpenClaw, Hermes: 20+ Channels)
- **Automatisiertes Lernen** (Hermes: Skills, Memory, Self-Improvement)
- **Multi-Modal** (Grok: Image, Video, Voice)
- **Produktive Consumer-UI** (alle anderen haben etwas, Eidolon hat Fragmente)

### Strategischer Pfad:
> Eidolon ist **nicht** ein Chatbot mit Features.
> Eidolon ist **ein agentisches Betriebssystem** mit kanonischem Kernel.
> Die anderen bauen **Assistenten**.
> Eidolon baut **eine Infrastruktur für autonome Arbeit**.

---

## 10. Empfehlung

Wenn Eidolon die nächste Evolutionsstufe zu OpenClaw/Hermes sein will:

1. **Kanonischen Kernel als Differenziator nutzen** — das haben die anderen nicht
2. **Multi-Channel via Hermes/OpenClaw-Pattern** — Gateway + Channel-Adapter
3. **Consumer-Entry ausbauen** — Chat-Entry wie ChatGPT/Perplexity
4. **Learning-Loop aus Hermes adaptieren** — automatische Skill-Erstellung
5. **Signature Object integrieren** — als eingebettete Identitäts-Präsenz

> Eidolon ist **besser fundiert** als die anderen, aber **sichtbar hinterher**.
> Der nächste Schritt ist nicht mehr Kernel-Arbeit, sondern **Consumer-Sichtbarkeit**.
