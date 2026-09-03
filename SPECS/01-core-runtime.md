# SPEC 01: Core Runtime

## Ziel
Der Agent-Kern: Event-Loop, Task-Orchestrierung, Model-Routing, Lebenszyklus.

## 1. Agent-State-Machine

```
States:
  IDLE        — Wartet auf Tasks
  THINKING    — Verarbeitet eine Nachricht
  PLANNING    — Erstellt einen Task-Plan
  EXECUTING   — Führt Skills aus
  EVALUATING  — Bewertet das Ergebnis
  SLEEPING    — Hiberniert (Modal/Daytona)
  ERROR       — Fehlerzustand, versucht Replanning
  SHUTTING_DOWN — Sauberes Beenden

Transitions:
  IDLE → THINKING (Nachricht empfangen)
  THINKING → PLANNING (Task erkannt)
  THINKING → IDLE (Smalltalk, keine Aktion nötig)
  PLANNING → EXECUTING (Plan erstellt)
  PLANNING → THINKING (Plan unklar, nachfragen)
  EXECUTING → EVALUATING (Skills ausgeführt)
  EXECUTING → ERROR (Fehler aufgetreten)
  EVALUATING → IDLE (Task abgeschlossen)
  EVALUATING → ERROR (Bewertung fehlgeschlagen)
  ERROR → THINKING (Replan)
  ERROR → IDLE (Aufgeben, User benachrichtigen)
  IDLE → SLEEPING (Idle-Timeout)
  SLEEPING → THINKING (Wake-up Event)
```

## 2. Task-Modell

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Task {
    pub id: TaskId,
    pub description: String,
    pub priority: Priority,
    pub status: TaskStatus,
    pub plan: Option<Plan>,
    pub dependencies: Vec<TaskId>,
    pub created_at: i64,
    pub deadline: Option<i64>,
    pub max_budget: Option<Budget>,
    pub retry_count: u32,
    pub max_retries: u32,
    pub result: Option<TaskResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum TaskStatus {
    Pending,
    Planning,
    Ready,
    Executing,
    Evaluating,
    Completed(TaskResult),
    Failed(TaskError),
    Cancelled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Plan {
    pub steps: Vec<PlanStep>,
    pub estimated_duration: Duration,
    pub estimated_cost: f64,
    pub confidence: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlanStep {
    pub id: StepId,
    pub description: String,
    pub skill: Option<SkillRef>,
    pub input: JsonValue,
    pub expected_output: Option<JsonValue>,
    pub depends_on: Vec<StepId>,
}
```

## 3. Model-Router

```rust
#[derive(Debug, Clone)]
pub struct ModelProfile {
    pub id: ModelId,
    pub name: String,
    pub provider: Provider,
    pub cost_per_1k_input: f64,
    pub cost_per_1k_output: f64,
    pub avg_latency_ms: u32,
    pub context_window: u32,
    pub strengths: Vec<TaskType>,     // "reasoning", "coding", "summarization"
    pub weaknesses: Vec<TaskType>,
    pub supports_tools: bool,
    pub supports_vision: bool,
}

#[derive(Debug, Clone)]
pub struct RouterDecision {
    pub model: ModelId,
    pub reason: String,
    pub estimated_cost: f64,
}

// Routing-Logik:
// 1. Task-Type erkennen (Reasoning? Coding? Vision? Translation?)
// 2. Budget prüfen (max_kosten)
// 3. Latenz-Anforderung prüfen (schnell vs. gründlich)
// 4. Bestes Modell auswählen
// 5. Fallback-Kette definieren (wenn Modell ausfällt)
```

## 4. Event-Loop

```rust
pub struct AgentLoop {
    agent: Arc<AgentState>,
    event_rx: mpsc::Receiver<AgentEvent>,
    task_queue: PriorityQueue<Task>,
    running: Arc<AtomicBool>,
}

pub enum AgentEvent {
    MessageReceived(Message),
    TaskCompleted(TaskId, TaskResult),
    TaskFailed(TaskId, TaskError),
    SkillRegistered(SkillRef),
    WakeUp,
    Shutdown,
}
```

## 5. Interfaces

### 5.1 Nachrichten-Format (intern)
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub id: MsgId,
    pub sender: Sender,
    pub recipient: Recipient,
    pub content: Content,
    pub timestamp: i64,
    pub reply_to: Option<MsgId>,
    pub priority: MessagePriority,
}

pub enum Sender {
    User(UserId),
    Agent(AgentId),
    External { channel: ChannelType, id: String },
}

pub enum Content {
    Text(String),
    Structured(JsonValue),
    TaskRequest(TaskRequest),
    TaskResponse(TaskResponse),
    System(SystemMessage),
}
```

## 6. Testing

### Unit-Tests
- [ ] State-Machine: Alle Transitions funktionieren
- [ ] Task-Scheduler: Prioritäten, Abhängigkeiten, Retry
- [ ] Model-Router: Korrekte Auswahl basierend auf Task-Typ
- [ ] Event-Loop: Nachrichten-Verarbeitung, Timeout-Handling

### Integration-Tests
- [ ] End-to-End: Nachricht → Plan → Ausführung → Antwort
- [ ] Model-Fallback: Modell-Ausfall → Retry mit anderem Modell
- [ ] Parallel-Tasks: 3 Tasks gleichzeitig, alle erfolgreich
