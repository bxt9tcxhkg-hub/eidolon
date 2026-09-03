# Eidolon vs New Target Truth Audit

> Audit basis: compare the **current Eidolon repo/runtime** against the active product and implementation truth:
> - `docs/eidolon-specification.md`
> - `docs/eidolon-product-identity.md`
> - `docs/eidolon-core-workflow.md`
> - `docs/eidolon-ui-workspace-architecture.md`
> - `docs/implementation-plan.md`
>
> This is a **truth audit**, not a roadmap fantasy. It separates:
> 1. what is already real
> 2. what is partially aligned
> 3. what is still missing or structurally weak
> 4. what threatens maintainability

---

## Plain verdict

**Eidolon is further along than this audit previously claimed, but it is still not yet at the full target product state.**

The stale version of this audit was wrong in one important way:

> it claimed the target operating kernel objects and `/api/v1` run/session routes were still missing.

That is no longer true.

What is true now:
- a real operate kernel exists
- real canonical records exist for sessions, runs, subagents, blockers, approvals, evidence, and transitions
- real `/api/v1` read and write routes exist for that kernel
- the UI and tests already depend on those routes

So the honest description is now:

> **Eidolon is no longer just a bridge toward the target kernel. The kernel exists. The remaining problem is coherence, phase preservation, consumer-facing compression, and maintainability.**

The strongest remaining gap is **not total absence of a kernel**.
The strongest remaining gap is this:

> **the product still expresses one truth through too many competing surfaces, payloads, and compatibility layers.**

---

## Fresh evidence basis

### Tests
```text
python -m pytest -q
107 passed, 3 warnings

python -m pytest -q tests/test_operate_kernel_contracts.py tests/test_operate_ui_contracts.py tests/test_web_ui_contracts.py
68 passed, 3 warnings

python -m pytest -q --collect-only
107 tests collected in 1.10s
```

### Live runtime
```text
curl http://127.0.0.1:8002/health
-> status: ok

curl http://127.0.0.1:8002/api/v1/operate/overview
-> ok: true
```

### Route shape checked now
```text
route_count 130
```

Verified relevant routes include:
```text
/api/v1/session/current
/api/v1/session/sync-from-workspaces
/api/v1/runs/current
/api/v1/runs/{run_id}/advance
/api/v1/runs/{run_id}/approval/{gate_id}
/api/v1/runs/{run_id}/approvals
/api/v1/runs/{run_id}/blockers
/api/v1/runs/{run_id}/blockers/{blocking_issue_id}/resolve
/api/v1/runs/{run_id}/evidence
/api/v1/runs/{run_id}/history
/api/v1/runs/{run_id}/interrupt
/api/v1/runs/{run_id}/next-action
/api/v1/runs/{run_id}/request-approval
/api/v1/runs/{run_id}/subagents
/api/v1/runs/{run_id}/transitions
/api/v1/runs/{run_id}/work-graph
/api/v1/operate/overview
/api/v1/operate/goals
/api/v1/operate/cycle
/api/v1/operate/derive
/api/v1/operate/revalidate
/identity
/health
/workspaces
/workspaces/context
/projects
/autonomy/status
/autonomy/goals
/autonomy/cycle
/evidence/summary
/bots/roles
```

### Key file-size evidence checked now
```text
70 lines   C:/Users/muham/eidolon/python/agent_server.py
95 lines   C:/Users/muham/eidolon/python/eidolon/operate_api_action_routes.py
72 lines   C:/Users/muham/eidolon/python/eidolon/operate_api_read_routes.py
86 lines   C:/Users/muham/eidolon/python/eidolon/operate/service.py
50 lines   C:/Users/muham/eidolon/python/eidolon/operate/contract_run_records.py
```

Important correction:
- an earlier audit snapshot treated `agent_server.py` and `web/index.html` as huge active monolith hotspots
- current file evidence shows that those earlier counts are stale for the active paths we re-checked now
- maintainability risk still exists, but it must be described from current hotspots, not old numbers

---

## What is already aligned with the target

## 1. A canonical operating kernel is real
This is now verified, not aspirational.

### Evidence
Contract records exist:
- `WorkSessionRecord`
- `ObjectiveRecord`
- `AgentRunRecord`
- `SubAgentRunRecord`
- `ApprovalGateRecord`
- `BlockingIssueRecord`
- `EvidenceItemRecord`
- `TransitionEventRecord`
- `NextActionRecord`

Files:
- `python/eidolon/operate/contract_session_records.py`
- `python/eidolon/operate/contract_run_records.py`
- `python/eidolon/operate/contract_blocking_records.py`
- `python/eidolon/operate/contract_evidence_records.py`
- `python/eidolon/operate/contract_types.py`
- `python/eidolon/operate/contracts.py`

### Verdict
- **real and substantial alignment**
- this is now part of the active product kernel, not just target theory

---

## 2. A real run state machine exists
### Evidence
Current canonical run states:
- `understanding`
- `planning`
- `spawning_work`
- `acting`
- `waiting`
- `blocked`
- `verifying`
- `completed`
- `failed`
- `cancelled`

Current canonical phases:
- `understand`
- `plan`
- `execute`
- `verify`
- `finalize`

Files:
- `python/eidolon/domain/mission/contracts.py`
- `python/eidolon/domain/mission/state_machine.py`
- `python/eidolon/operate/contract_transitions.py`

### Verdict
- **real and useful**
- stronger than the old audit admitted

### Remaining gap
- phase preservation against the full 8-step product workflow is still too implicit
- the runtime has phases, but the user-facing product semantics are not yet fully enforced end-to-end

---

## 3. The `/api/v1` operating surface exists and is active
### Evidence
Read routes exist for:
- current session
- current run
- subagents
- evidence
- transitions
- blockers
- approvals
- next action
- history
- work graph
- operate overview

Write routes exist for:
- workspace-to-session sync
- run advance
- approval request
- blocker resolution
- approval resolution
- interrupt

Files:
- `python/eidolon/operate_api_read_routes.py`
- `python/eidolon/operate_api_action_routes.py`

### Verdict
- **real and active**
- this should now be treated as the canonical operating API family

### Remaining gap
- some compatibility and older route families still compete with it conceptually
- overview is too broad for a consumer-first front door

---

## 4. Subagent, blocker, approval, evidence, and transition plumbing is real
### Evidence
- store/service tests round-trip all major records
- operate flow tests verify workspace execution creates real subagent lifecycle and operate snapshot
- current live overview payload includes:
  - session
  - objective
  - run
  - subagents
  - evidence
  - next action
  - work graph

### Verdict
- **real subsystem, not placebo**

### Remaining gap
- many live subagent rows are still generic `Workspace Action` entries
- the product can truthfully claim subagent execution exists
- it cannot yet fully claim a richly differentiated specialist model everywhere

---

## 5. Product identity and chat-first direction are real
### Evidence
- spec still says chat is the fixed start surface
- UI contract tests verify chat is the initial active surface
- current product docs frame Eidolon as a central work-leading system, not merely a tool box

### Verdict
- **aligned in direction and partially realized**

### Remaining gap
- front-door payloads and surrounding support surfaces still leak too much system structure

---

## 6. Anti-placebo discipline remains a major strength
### Evidence
Current tests cover truths such as:
- role templates not falsely presented as active
- health not falsely claiming QUIC when absent
- chat UI not falling back to fake success copy
- code-fix proposal not claimed as applied
- workspace and operate endpoints exposing real state
- compatibility routes marked and bounded by real behavior

### Verdict
- **major strength**

---

## What is only partially aligned

## 7. The product kernel exists, but product truth is still fragmented
### Evidence
The runtime still speaks through several overlapping layers:
- operate kernel
- workspace context summary
- autonomy compatibility views
- goals compatibility surface
- older status/support views

The live overview payload also includes a large amount of historical/deep state.

### Verdict
- **partially aligned**

### Why this matters
The system already has the right core objects, but the product still often feels like several adjacent systems rather than one dominant work stream.

---

## 8. Phase continuity exists technically, but not yet strongly enough in the product contract
### Evidence
The spec requires these semantic phases to remain meaningful:
1. Chat-Einstieg
2. Verständnis- und Strukturaufbau
3. Kontextklassifikation
4. Projektbildung
5. Workspace-Komposition
6. Rollenbildung
7. Ausführung
8. Verifikation und Rückkehr

Current runtime states are real, but these product phases are not yet all explicit first-class outputs everywhere.

### Verdict
- **partially aligned**

### Gap
A future refactor could compress the runtime in a technically valid way while silently dropping product semantics unless tests/docs are tightened.

---

## 9. Consumer-facing compression is still weaker than the target demands
### Evidence
The live `GET /api/v1/operate/overview` response captured in this audit path was extremely large because it aggregated deep subagent/evidence/work-graph material.

### Verdict
- **partial alignment**

### Gap
Truth is present, but the front door still risks feeling like a data exhaust surface rather than a compact consumer-friendly operating entry.

---

## 10. Specialist semantics are still underdeveloped compared to the target story
### Evidence
Live subagent rows show many instances like:
- `display_name: Workspace Action`
- `function_type: board:add_card`
- `function_type: board:set_priority`

### Verdict
- **partial alignment**

### Gap
That proves real execution and real evidence, but it is still weaker than the intended model of semantically meaningful planner/researcher/builder/verifier/resolver specialists.

---

## What is still missing or weak

## 11. One uncontested operating truth across all surfaces
This is now the top product gap.

### What exists
- a real kernel
- real `/api/v1` routes
- real UI integrations

### What is still weak
- compatibility layers can still pull attention back to older mental models
- chat, workspace, operate, goals, and support views are not yet fully subordinated to one shared primary work narrative

### Verdict
- **missing in product coherence, not missing in raw capability**

---

## 12. Explicit phase-preservation enforcement
### What exists
- runtime phases and states
- transition rules
- spec-level workflow

### What is missing
- explicit regression tests that guarantee the 8 product phases remain mappable and visible after refactors
- explicit user-facing payload fields for some of the intermediate semantic phases

### Verdict
- **missing, high priority**

---

## 13. Overview payload discipline
### What exists
- a truthful all-in-one overview route

### What is missing
- compact serializers/view models for the front door
- deep-history lazy loading by separate endpoints
- bounded counts/pagination defaults at the first entry surface

### Verdict
- **missing, high priority**

---

## 14. Stronger specialist subagent semantics
### What exists
- real child runs
- real evidence
- real state transitions

### What is missing
- stronger controlled specialist vocabulary
- clearer mission semantics
- better UI explanation of why a child run exists

### Verdict
- **missing, medium-high priority**

---

## 15. Maintainability alignment with the new product truth
This now needs a more precise statement than "the repo is monolithic".

### What is good
- active operate contracts are split into focused files
- route families are already separated into read vs action modules
- service and store layers exist
- tests cover critical truth behaviors

### What is bad
- multiple product truth layers still coexist
- compatibility routes and compatibility thinking still add conceptual drag
- some payloads are too broad
- maintainability is still at risk if modularization happens before phase/contract locking

### Verdict
- **moderate maintainability, improving architecture direction**

### Important nuance
The right maintainability move now is **not** a blind rewrite.
It is:
1. freeze the canonical contract vocabulary
2. preserve product phases in tests/docs
3. slim and separate high-noise payloads
4. only then continue larger modularization passes

---

## Fit score against the new target

This is not a hype score. It is an implementation-fit score as of the evidence above.

| Area | Fit now | Verdict |
|---|---:|---|
| Product identity direction | 8/10 | strong direction, still needs cleaner front-door compression |
| Chat-first entry | 7/10 | real, but surrounding product worlds still compete |
| Canonical operating kernel | 8/10 | real and already significant |
| Run state machine | 8/10 | real, but product-phase mapping needs stronger preservation |
| `/api/v1` operating API | 8/10 | real and active |
| Subagent execution reality | 7/10 | real child runs exist |
| Specialist subagent semantics | 4/10 | still too generic in live examples |
| Approvals / blockers / evidence / transitions | 8/10 | first-class and real |
| Consumer-friendly front-door compression | 4/10 | truthful but too broad/noisy |
| Single work-leading center of gravity | 5/10 | direction is right, coherence still incomplete |
| Anti-placebo truth hardening | 9/10 | major strength |
| Maintainability alignment | 6/10 | improving, but still threatened by compatibility and payload drift |

---

## Priority gaps now

## P0 — Truth-source and stale-claim cleanup
- old audits/plans must stop claiming the operating kernel is absent
- `/api/v1` must be treated consistently as canonical product truth
- current docs must not drag the project back toward obsolete center-of-gravity narratives

## P1 — Phase-preserving coherence
- preserve the 8 product phases explicitly
- unify chat/workspace/operate continuity more strongly
- ensure refactors cannot erase product semantics

## P1 — Consumer compression without truth loss
- slim `GET /api/v1/operate/overview`
- keep deep state reachable, but not dumped into the front door
- make current objective/run/next action the dominant surface truth

## P2 — Specialist semantics and compatibility cleanup
- strengthen specialist child-run meaning
- continue shrinking compatibility surface dominance
- demote support worlds to support status

## P2 — Maintainability hardening
- modularize only after contract equivalence is tested
- align code shape to product shape
- reduce conceptual duplication, not just file size

---

## Recommended consolidation order
1. Keep `docs/implementation-plan.md` as the active implementation canon
2. Update this audit so it reflects the real existing kernel
3. Add phase-preservation regression tests
4. Slim and restructure `/api/v1/operate/overview`
5. Strengthen session/context continuity fields
6. Strengthen specialist subagent semantics
7. Continue UI consolidation around current objective + run + next action
8. Only then do broader modularization passes

---

## Final verdict

**Eidolon is now beyond the point where it can honestly be described as lacking a work kernel.**

That part is real.

What is not solved yet is the harder product problem:

> **making that real kernel feel like one coherent, consumer-friendly, phase-preserving, maintainable work-leading system instead of a truthful but still fragmented set of adjacent surfaces.**

That is the real distance from current state to target state now.
