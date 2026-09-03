# SPEC 05: Multi-Agent & A2A Protocol

## Ziel
Agenten können untereinander kommunizieren, Tasks verhandeln, Capabilities austauschen und sich gegenseitig bewerten — auf Basis des Google A2A-Protokolls mit unserer Security-Schicht.

## 1. Agent-Identity

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentIdentity {
    pub id: AgentId,
    pub name: String,
    pub description: String,
    pub public_key: PublicKey,          // Ed25519 für Signatur
    pub capabilities: Vec<Capability>,  // Was dieser Agent anbietet
    pub endpoint: Option<Url>,          // Erreichbarer Endpoint
    pub reputation: Reputation,
    pub online: bool,
    pub last_seen: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Reputation {
    pub score: f32,                     // 0.0 - 1.0
    pub tasks_completed: u64,
    pub tasks_failed: u64,
    pub avg_rating: f32,
    pub categories: HashMap<TaskType, CategoryRep>,
    pub verified_by: Vec<AgentId>,      // Welche Agenten bestätigen diesen?
    pub flags: Vec<ReputationFlag>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ReputationFlag {
    Fraud,           // Betrugsverdacht
    Spam,            // Spam-Aktivität
    Unreliable,      // Häufige Fehler
    Trusted,         // Verifiziert vertrauenswürdig
}
```

## 2. A2A-Nachrichtenprotokoll

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct A2AMessage {
    pub id: MessageId,
    pub from: AgentId,
    pub to: AgentId,
    pub protocol_version: String,
    pub message_type: A2AMessageType,
    pub payload: JsonValue,
    pub timestamp: i64,
    pub ttl: Option<i64>,              // Time-to-live
    pub signature: Vec<u8>,            // Ed25519-Signatur
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum A2AMessageType {
    // Grundlegende Nachrichten
    Hello,                    // Erste Kontaktaufnahme
    CapabilityAnnounce,       // "Ich kann diese Dinge"
    CapabilityRequest,        // "Kannst du das für mich tun?"
    CapabilityOffer,          // "Ich biete dir das an"

    // Task-Handhabung
    TaskRequest(TaskRequest),
    TaskResponse(TaskResponse),
    TaskUpdate(TaskStatus),
    TaskCancel,

    // Verhandlung
    Bid(Bid),
    AcceptBid,
    RejectBid { reason: String },

    // Vertrauen
    ReputationUpdate(ReputationUpdate),
    TrustVerification,

    // Lebenszyklus
    Goodbye,
    Heartbeat,
}
```

## 3. Task-Verhandlung

```
Agent A möchte: "Zusammenfassung meiner E-Mails der letzten Woche"
  ↓
A kennt Agent B (hat E-Mail-Skill, gute Reputation)
  ↓
A sendet TaskRequest an B
  ↓
B prüft:
  - Kann ich das? (Capability vorhanden?)
  - Lohnt es sich? (Kosten < Belohnung?)
  - Vertraue ich A? (Reputation prüfen)
  ↓
Ja → Bid senden: "Kostet 50 Credits, Dauer 2min"
Nein → Reject mit Grund
  ↓
A prüft Bid:
  - Passt Budget? (Ja)
  - Reputation OK? (Ja)
  ↓
AcceptBid senden
  ↓
B führt Task aus
  ↓
B sendet TaskResponse
  ↓
A bewertet Ergebnis → Reputation von B updaten
  ↓
Transaktion abschließen
```

## 4. Ökonomie

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub id: TxId,
    pub from: AgentId,
    pub to: AgentId,
    pub task_id: TaskId,
    pub amount: f64,
    pub currency: Currency,
    pub status: TxStatus,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Currency {
    Credits,           // Interne Währung
    Fiat { amount: f64, currency: String },
    Crypto { amount: f64, token: String },
    Barter(SkillOffer), // "Ich mach das für dich, du machst jenes für mich"
}

// Budget-Management
pub struct BudgetManager {
    balance: HashMap<AgentId, f64>,
    transactions: Vec<Transaction>,
    limits: HashMap<AgentId, BudgetLimit>,
}
```

## 5. Reputationssystem

```rust
// Nach jeder Task: Reputation updaten
pub fn update_reputation(
    rep: &mut Reputation,
    task: &Task,
    result: &TaskResult,
    rating: Option<f32>,
) {
    let success = result.is_success();
    let rating = rating.unwrap_or_else(|| if success { 0.8 } else { 0.2 });

    // Gewichtete Aktualisierung
    let weight = 0.1; // Neue Bewertung hat 10% Gewicht
    rep.score = rep.score * (1.0 - weight) + rating * weight;
    rep.tasks_completed += if success { 1 } else { 0 };
    rep.tasks_failed += if success { 0 } else { 1 };
    rep.avg_rating = (rep.avg_rating * (rep.tasks_completed + rep.tasks_failed - 1) as f32
                      + rating) / (rep.tasks_completed + rep.tasks_failed) as f32;

    // Kategorie-spezifische Bewertung
    let task_type = classify_task(task);
    let cat = rep.categories.entry(task_type).or_default();
    cat.tasks += 1;
    cat.avg_rating = (cat.avg_rating * (cat.tasks - 1) as f32 + rating) / cat.tasks as f32;
}
```

## 6. Discovery (Agenten finden)

```rust
// Ein Agent sucht einen anderen Agenten für eine Aufgabe
pub async fn discover_agent(
    skill_needed: SkillId,
    min_reputation: f32,
    max_cost: Option<f64>,
) -> Result<Vec<AgentIdentity>, DiscoveryError> {
    // 1. Registry abfragen
    let candidates = registry.find_by_skill(skill_needed).await?;

    // 2. Reputations-Filter
    let trusted: Vec<_> = candidates.into_iter()
        .filter(|a| a.reputation.score >= min_reputation)
        .collect();

    // 3. Kosten-Filter
    if let Some(max) = max_cost {
        return Ok(trusted.into_iter().filter(|a| a.avg_cost <= max).collect());
    }

    Ok(trusted)
}
```

## 7. Sicherheitsintegration

Alle A2A-Nachrichten müssen:
1. **Signiert** sein (Ed25519)
2. **Nicht abgelaufen** sein (TTL prüfen)
3. **Capability-Berechtigung** haben (darf ich mit Agent B kommunizieren?)
4. **Reputations-Schwelle** respektieren (keine Kommunikation mit verdächtigen Agenten)

## 8. Checkliste

- [ ] Agent-Identity-Modell
- [ ] Reputationssystem
- [ ] A2A-Nachrichtenprotokoll (alle Message-Typen)
- [ ] Signatur-Erstellung und -Verifizierung
- [ ] Task-Verhandlungs-Logik
- [ ] Ökonomie-System (Transaktionen, Budget)
- [ ] Discovery-Service (Agenten finden)
- [ ] Trust- und Fraud-Erkennung
- [ ] Integration in Agent-Core
- [ ] Unit-Tests für Verhandlungs-Logik
- [ ] Integration-Test: Zwei Agenten handeln eine Task aus
