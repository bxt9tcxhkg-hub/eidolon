# Eidolon Implementation Package — Operating Kernel without Phase Loss

> Status: active implementation package for the current Eidolon product direction.
>
> This document replaces the old `Implementation Plan: Eidolon Evolutionstufe 3` plan, which described a different product center of gravity (P2P / economy / overlay first) and is no longer the correct build order for Eidolon as defined in `docs/eidolon-specification.md`.
>
> This package is implementation truth for the **migration path** from the current repo/runtime to the target product model. It does **not** claim the target is already complete.

## 1. Source-of-truth hierarchy
1. **Product Soll**: `docs/eidolon-specification.md` and linked contract docs
2. **This document**: canonical build package from current truth to target kernel
3. **Audit / Mapping**: `docs/eidolon-vs-new-target-truth-audit.md` and findings docs
4. **Live runtime and tests**: what is currently real
5. **Historical plans**: reference only

## 2. Non-negotiable rules
- No placebo state
- No placeholder functionality shown as real
- No fake success messages
- No UI control without a real event path
- No backend object without a stable UI meaning
- No new surface that drops or bypasses the main workflow phases
- No migration that loses project/session/run continuity

## 3. Core product rule: no phase loss
Eidolon's main workflow from `docs/eidolon-core-workflow.md` remains binding:

1. Chat-Einstieg
2. Verständnis- und Strukturaufbau
3. Kontextklassifikation
4. Projektkandidat oder aktives Projekt ableiten
5. geeignete Arbeitsoberfläche zusammensetzen
6. Bots und Verantwortlichkeiten ableiten, falls nötig
7. Arbeit vorbereiten oder ausführen
8. Verifikation, Sichtbarkeit und nächste Schritte bereitstellen

### Phase-preservation contract
The implementation may rename, compress, or regroup technical states, but it may **not** lose these semantic phases.

Every request, run, interruption, approval, blocker, and completion must remain mappable to this flow.

## 4. Verified current truth
The current repo/runtime already contains more of the target kernel than older planning text claimed.

### Verified in code
Existing contract objects already exist under `python/eidolon/operate/`:
- `WorkSessionRecord`
- `ObjectiveRecord`
- `AgentRunRecord`
- `SubAgentRunRecord`
- `ApprovalGateRecord`
- `BlockingIssueRecord`
- `EvidenceItemRecord`
- `TransitionEventRecord`
- `NextActionRecord`

Existing run/state semantics already exist:
- `AgentRunState`: `understanding`, `planning`, `spawning_work`, `acting`, `waiting`, `blocked`, `verifying`, `completed`, `failed`, `cancelled`
- `AgentRunPhase`: `understand`, `plan`, `execute`, `verify`, `finalize`
- transition validators for runs and subagents
- `OperateStore` schema with real SQLite tables for sessions, objectives, runs, subagents, blockers, approvals, transitions, evidence

### Verified in routes
Current API already exposes:
- `GET /api/v1/session/current`
- `POST /api/v1/session/sync-from-workspaces`
- `GET /api/v1/runs/current`
- `GET /api/v1/runs/{run_id}/subagents`
- `GET /api/v1/runs/{run_id}/evidence`
- `GET /api/v1/runs/{run_id}/transitions`
- `GET /api/v1/runs/{run_id}/blockers`
- `GET /api/v1/runs/{run_id}/approvals`
- `GET /api/v1/runs/{run_id}/next-action`
- `GET /api/v1/runs/{run_id}/history`
- `GET /api/v1/runs/{run_id}/work-graph`
- `POST /api/v1/runs/{run_id}/advance`
- `POST /api/v1/runs/{run_id}/request-approval`
- `POST /api/v1/runs/{run_id}/blockers/{blocking_issue_id}/resolve`
- `POST /api/v1/runs/{run_id}/approval/{gate_id}`
- `POST /api/v1/runs/{run_id}/interrupt`
- `GET /api/v1/operate/overview`

### Verified live
- `curl http://127.0.0.1:8002/api/v1/operate/overview` returned `ok: true`
- live payload included real:
  - session
  - objective
  - run
  - subagents
  - evidence
  - next_action
  - work_kernel context
- targeted tests passed:
  - `tests/test_operate_kernel_contracts.py`
  - `tests/test_operate_ui_contracts.py`
  - `tests/test_web_ui_contracts.py`
- Result: `68 passed, 3 warnings`

## 5. Verified current gaps
This is the real gap list now — not the stale earlier one.

### G1. The kernel exists, but product truth is still split
The target objects exist, but the product still splits truth across:
- chat context
- workspace/project state
- operate snapshot
- autonomy/goal compatibility layers
- older status surfaces

### G2. Phase continuity is implicit, not explicit enough
The workflow phases from the product spec are not yet first-class and visible end-to-end.
Current code has runtime states and phases, but not a clean user-facing mapping for:
- project candidate
- workspace composition
- responsibility derivation
- approval / interruption re-entry

### G3. `/api/v1/operate/overview` is too broad for a consumer-first front door
Live evidence showed a very large payload (~620k chars in the captured run) because overview currently aggregates deep historical subagent/evidence/work-graph material.
That is truth-preserving, but it is not consumer-friendly and should not be the default entry payload.

### G4. Subagent model is real, but semantically weak
Subagents exist, but many live examples are generic `Workspace Action` records. That proves the plumbing, but not yet the intended differentiated specialist model.

### G5. Compatibility layers still compete with the target kernel
Legacy or compatibility routes/surfaces around autonomy, workspace summaries, status, and older top-level navigation still compete with the target mental model.

### G6. UI still over-exposes system worlds
The frontend has moved toward chat-first, but the backend and view model still make it too easy to render:
- operate
- goals
- status
- mesh/devices
- healing
- settings
as parallel worlds instead of subordinate views of one work-leading kernel.

## 6. Product target, restated in implementation terms
Eidolon must become a **work-leading operating kernel** with these rules:

### What the user enters through
- Chat is always the front door.
- The front door shows only the minimum truth needed to continue work.

### What the system is centered on
- one `WorkSession`
- one active `Objective`
- one active `AgentRun`
- zero or more `SubAgentRun`s
- explicit `ApprovalGate`s
- explicit `BlockingIssue`s
- explicit `EvidenceItem`s
- explicit `TransitionEvent`s
- one `NextAction`

### What the UI is centered on
Not tabs as the primary truth.
The primary truth is:
- what we are doing
- where it stands
- who is doing it
- what is blocked
- what needs approval
- what was verified
- what should happen next

## 7. Canonical phase model without loss
The target implementation must preserve the product's eight-phase workflow while mapping it onto run states.

### 7.1 Product phases
| Product phase | Meaning | Must remain visible? |
|---|---|---|
| Chat-Einstieg | user initiates or resumes work | yes |
| Verständnis- und Strukturaufbau | system clarifies goal and scope | yes |
| Kontextklassifikation | chat topic / project candidate / active project | yes |
| Projektbildung | candidate becomes explicit objective/project | yes |
| Workspace-Komposition | right surface is assembled from work mode | yes |
| Rollenbildung | responsibilities / subagents are derived if needed | yes |
| Ausführung | work happens | yes |
| Verifikation und Rückkehr | verified result + next step | yes |

### 7.2 Runtime mapping
| Product phase | Current canonical runtime field(s) | Required strengthening |
|---|---|---|
| Chat-Einstieg | `WorkSession.source_kind`, chat entry UI | bind directly to active session and run bootstrap |
| Verständnis- und Strukturaufbau | `AgentRun.state=understanding`, `current_phase=understand` | expose structured understanding artifact |
| Kontextklassifikation | `work_kernel.workflow_state`, workspace context, context model | unify candidate/active classification in run-owned contract |
| Projektbildung | `ObjectiveRecord`, workspace bootstrap | explicit candidate-to-objective transition record |
| Workspace-Komposition | `current_view`, workspace bridge, overview payload | make surface choice an explicit transition with rationale |
| Rollenbildung | `SubAgentRunRecord` creation | enforce semantic specialist types, not generic actions only |
| Ausführung | `planning`, `spawning_work`, `acting`, `waiting`, `blocked` | keep user-visible reason and owner at all times |
| Verifikation und Rückkehr | `verifying`, `completed`, evidence, next_action | make completion summary compact and front-door friendly |

### 7.3 Rule
No refactor may collapse the model into only:
- `understanding`
- `acting`
- `done`

That would lose the product's core semantics.

## 8. Canonical contracts to keep and strengthen
The correct move is **not** to throw away the current operate kernel. The correct move is to harden and unify it.

### Keep
- `WorkSessionRecord`
- `ObjectiveRecord`
- `AgentRunRecord`
- `SubAgentRunRecord`
- `ApprovalGateRecord`
- `BlockingIssueRecord`
- `EvidenceItemRecord`
- `TransitionEventRecord`
- `NextActionRecord`

### Strengthen
#### `WorkSessionRecord`
Add or confirm:
- active context kind: `chat_topic | project_candidate | active_project`
- entry message id / source event id
- linked workspace id (optional)
- current surface reason

#### `ObjectiveRecord`
Add or confirm:
- candidate source
- acceptance state
- goal confidence / clarification completeness
- relationship to project record if one exists

#### `AgentRunRecord`
Add or confirm:
- visible product phase
- phase provenance
- summary artifact refs
- current owner (`eidolon` or child)
- compact completion summary

#### `SubAgentRunRecord`
Add or confirm:
- specialist type from controlled vocabulary
- explicit deliverable type
- provenance of spawn decision
- whether user can interact with it directly

#### `ApprovalGateRecord`
Add or confirm:
- user-visible consequence of approve/reject
- related evidence ids
- expiry semantics

#### `BlockingIssueRecord`
Add or confirm:
- blocker owner path
- resolution action type
- can system continue partially?

#### `EvidenceItemRecord`
Add or confirm:
- evidence severity / confidence
- whether it is completion-grade evidence
- compact UI digest text

#### `TransitionEventRecord`
Add or confirm:
- product-phase delta
- interrupt classification: refine / conflict / supersede
- whether the transition changed user-visible next action

## 9. API architecture package
The `/api/v1` namespace already exists. The task now is to make it the uncontested operating truth.

## 9.1 Keep as canonical read API
- `GET /api/v1/session/current`
- `GET /api/v1/runs/current`
- `GET /api/v1/runs/{id}/subagents`
- `GET /api/v1/runs/{id}/evidence`
- `GET /api/v1/runs/{id}/transitions`
- `GET /api/v1/runs/{id}/blockers`
- `GET /api/v1/runs/{id}/approvals`
- `GET /api/v1/runs/{id}/next-action`
- `GET /api/v1/runs/{id}/history`
- `GET /api/v1/runs/{id}/work-graph`

## 9.2 Keep as canonical write API
- `POST /api/v1/session/sync-from-workspaces`
- `POST /api/v1/runs/{id}/advance`
- `POST /api/v1/runs/{id}/request-approval`
- `POST /api/v1/runs/{id}/blockers/{blocking_issue_id}/resolve`
- `POST /api/v1/runs/{id}/approval/{gate_id}`
- `POST /api/v1/runs/{id}/interrupt`

## 9.3 Split the current overview endpoint
`GET /api/v1/operate/overview` should remain, but it must become a **compact orchestrator payload**, not a giant everything dump.

### New overview contract target
Overview should contain only:
- compact session summary
- compact objective summary
- compact run summary
- active blockers summary
- active approvals summary
- active subagents summary
- compact next action
- compact work kernel summary
- pointers/counts to deeper endpoints

### Must move out of overview
- full evidence history
- full transition history
- full subagent archive
- full work graph expansion
- verbose workspace mutation payloads

## 10. UI architecture package

### 10.1 Front door
The default screen remains chat-first.
The front door may show only:
- current objective
- current run state
- approval needed?
- blocked?
- who is acting?
- next step
- one compact recent verification/result capsule

### 10.2 Operate view
Operate becomes the structured truth surface for deeper work, but stays subordinate to the chat-led entry.

### 10.3 Workspace view
Workspace is not a separate product kingdom. It is one projection of the current objective/run.

### 10.4 Goals/status/mesh/healing/settings
These must become:
- supporting views
- settings/ops support
- never the primary mental model of the product

## 11. Detailed implementation structure

## P0 — Canonical kernel consolidation
Goal: keep the current kernel, remove ambiguity, preserve phases.

- [ ] Mark `docs/implementation-plan.md` as the active implementation canon for this migration
- [ ] Re-audit `docs/eidolon-vs-new-target-truth-audit.md` against the current operate kernel so it stops claiming missing pieces that already exist
- [ ] Inventory all route families that still duplicate or compete with `/api/v1`
- [ ] Inventory all frontend surfaces still reading non-canonical state for work truth
- [ ] Define one canonical mapping from product phases to runtime states and publish it in code comments/tests
- [ ] Add regression tests that fail if a product phase becomes unmappable

### P0 exit criteria
- one implementation canon
- no stale doc claiming the kernel objects are absent
- product phases explicitly preserved in tests and docs

## P1 — Session and context unification
Goal: make chat, objective, run, and workspace continuity explicit.

- [ ] Extend `WorkSessionRecord` with explicit context classification fields
- [ ] Extend `ObjectiveRecord` with candidate-to-objective provenance
- [ ] Ensure chat entry can always resolve the active session and active run without fallback ambiguity
- [ ] Ensure workspace sync updates the same session/run truth instead of parallel summary worlds
- [ ] Add tests for:
  - new topic -> chat topic
  - project candidate -> objective creation
  - active project -> resumed run
  - interrupt -> revised but continuous session

### P1 exit criteria
- session continuity survives chat, workspace, and operate transitions
- no silent context fork

## P2 — Run-phase strengthening
Goal: make the eight-phase product workflow explicit in the kernel.

- [ ] Add explicit user-visible phase mapping to run payloads
- [ ] Record candidate formation and workspace composition as transition events
- [ ] Distinguish `planning` from `awaiting_approval` and `blocked` more clearly in UI payloads
- [ ] Add interrupt classification (`refine`, `conflict`, `supersede`) to transitions
- [ ] Add completion summary artifact support to `AgentRunRecord` or adjacent view model
- [ ] Add tests that verify phase continuity after blocker resolution and approval decisions

### P2 exit criteria
- every major run can be read as a coherent phase narrative
- interruptions do not erase work history or phase meaning

## P3 — Specialist subagent hardening
Goal: move from generic execution records to meaningful specialist runs.

- [ ] Define controlled specialist families:
  - planner
  - researcher
  - builder
  - verifier
  - resolver
  - operator
  - monitor
  - reconciler
- [ ] Keep generic workspace actions only as low-level execution evidence, not the main subagent story
- [ ] Spawn semantically named specialist runs where the product claims specialist work
- [ ] Add direct link between specialist mission and completion evidence
- [ ] Add UI summaries that explain why each specialist exists
- [ ] Add tests that product surfaces do not imply rich specialists when only generic action rows exist

### P3 exit criteria
- visible subagents have meaningful roles
- product does not overclaim specialization

## P4 — Overview payload slimming
Goal: consumer-friendly front door without losing truth.

- [ ] Introduce compact serializers / view models for overview
- [ ] Move deep history to dedicated endpoint fetches only
- [ ] Bound overview evidence/subagent/history counts
- [ ] Add count + pagination metadata where needed
- [ ] Ensure chat entry fetches only compact truth first
- [ ] Add payload-size regression tests for overview

### P4 exit criteria
- `GET /api/v1/operate/overview` is compact
- front door stays fast and readable
- no truth loss: deep data remains reachable through dedicated endpoints

## P5 — UI hierarchy consolidation
Goal: one work-leading center of gravity.

- [ ] Make current objective/run the primary object on chat entry
- [ ] Keep Operate as the deeper truth surface
- [ ] Relegate goals/status/mesh/healing/settings to support layers
- [ ] Remove or demote copy that frames these as equal product worlds
- [ ] Make next action the dominant action affordance
- [ ] Make blocker/approval state impossible to miss without relying on tiny color signals
- [ ] Ensure workspace views are labeled as views of current work, not separate systems

### P5 exit criteria
- users perceive one active work stream, not a tool zoo

## P6 — Compatibility cleanup
Goal: stop legacy layers from re-fragmenting the product.

- [ ] Audit autonomy compatibility routes and identify which are still needed as adapters
- [ ] Mark deprecated route families explicitly in payloads/docs where retained
- [ ] Route new UI work only through canonical `/api/v1` contracts
- [ ] Remove duplicate state assembly paths once replacement is verified
- [ ] Add tests to ensure deprecated paths cannot become the sole source for UI truth again

### P6 exit criteria
- `/api/v1` is uncontested for operating truth
- legacy surfaces cannot silently pull the product backward

## P7 — Evidence and verification hardening
Goal: no false completion and no invisible failures.

- [ ] Require completion-grade evidence for `completed/success`
- [ ] Differentiate `success`, `warning`, `failure` consistently across run and subagent outputs
- [ ] Ensure every approval/blocker resolution emits transition + evidence where appropriate
- [ ] Add tests that UI success copy is impossible without backend verification
- [ ] Add live smoke checks for:
  - create objective
  - advance run
  - request approval
  - resolve blocker
  - fetch overview

### P7 exit criteria
- no visible success without evidence-backed state

## P8 — Modularization after truth is stable
Goal: reduce monolith pressure without breaking meaning.

- [ ] Split route registration by canonical domains:
  - session
  - runs
  - approvals
  - blockers
  - evidence
  - transitions
  - overview
- [ ] Split frontend data access and rendering by same domains
- [ ] Keep one shared contract vocabulary across backend and frontend
- [ ] Modularize only after contract equivalence is covered by tests

### P8 exit criteria
- code shape reflects product shape
- modularization no longer risks semantic drift

## 12. File-level implementation map

### Backend contracts and state
- `python/eidolon/operate/contract_session_records.py`
- `python/eidolon/operate/contract_run_records.py`
- `python/eidolon/operate/contract_blocking_records.py`
- `python/eidolon/operate/contract_evidence_records.py`
- `python/eidolon/operate/contract_types.py`
- `python/eidolon/domain/mission/contracts.py`
- `python/eidolon/domain/mission/state_machine.py`

### Backend store/service
- `python/eidolon/operate/store.py`
- `python/eidolon/operate/store_*.py`
- `python/eidolon/operate/service.py`
- `python/eidolon/operate/service_objectives.py`
- `python/eidolon/operate/service_support.py`
- `python/eidolon/operate/bridge_*.py`
- `python/eidolon/operate/bridge_views.py`

### API surface
- `python/eidolon/operate_api_read_routes.py`
- `python/eidolon/operate_api_action_routes.py`
- compatibility layers under `python/eidolon/*compat*`
- `python/agent_server.py`

### Frontend
- `python/eidolon/web/chat-ui.js`
- `python/eidolon/web/operate-ui.js`
- `python/eidolon/web/operate-view-ui.js`
- `python/eidolon/web/operate-actions-ui.js`
- `python/eidolon/web/app-shell.js`
- `python/eidolon/web/index.html`
- shell/chat/component CSS files

### Tests
- `tests/test_operate_kernel_contracts.py`
- `tests/test_operate_ui_contracts.py`
- `tests/test_web_ui_contracts.py`
- add new focused tests for phase preservation and compact overview behavior

## 13. Verification gates
No phase may be declared complete without all three:

### Gate A — contract truth
- tests for records / transitions / API shape pass

### Gate B — runtime truth
- live endpoint check passes on running server

### Gate C — surface truth
- UI renders the state honestly and compactly

## 14. Immediate next implementation order
This is the concrete order that should be executed next.

1. Revalidate and update the stale truth-audit document
2. Add phase-preservation tests
3. Slim `GET /api/v1/operate/overview` into a compact front-door payload
4. Move deep history/evidence/subagent archive reads to dedicated lazy fetches
5. Strengthen session/context continuity fields
6. Strengthen specialist subagent semantics
7. Continue UI consolidation around current objective + run + next action
8. Only then do larger modularization passes

## 15. Plain verdict
Eidolon does **not** need a greenfield rewrite to reach the target.

The right path is:
- keep the real kernel that already exists
- stop stale docs from pretending it does not
- preserve all eight product phases explicitly
- compress the product around one work-leading truth
- remove payload, UI, and compatibility drift that still makes the system feel more fragmented than it really is
