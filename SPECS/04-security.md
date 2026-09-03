# SPEC 04: Security & Zero-Trust

## Ziel
Feingranulare, capability-basierte Sicherheit statt Alles-oder-Nichts. Jede Aktion wird protokolliert, jede Berechtigung ist verifizierbar.

## 1. Capability-System

```rust
// Eine Capability = ein verifizierbares Recht
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Capability {
    pub id: CapId,
    pub resource: Resource,
    pub actions: Vec<Action>,
    pub constraints: Constraints,
    pub issuer: AgentId,
    pub subject: Subject,        // Wer hat diese Capability
    pub issued_at: i64,
    pub expires_at: Option<i64>,
    pub signature: Vec<u8>,      // Ed25519-Signatur
    pub parent: Option<CapId>,   // Verkettung (Delegation)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Resource {
    File(PathPattern),           // "file:///tmp/*", "file://~/Documents/**"
    Shell(ShellCap),             // "shell:read", "shell:write", "shell:exec"
    Network(NetworkPattern),     // "web:https://*", "api:github.com/*"
    Database(DbPattern),         // "db:sqlite://*", "db:postgres://*"
    Skill(SkillId),              // Capability innerhalb eines Skills
    Agent(AgentId),              // Interaktion mit einem Agenten
    System(SystemAction),        // "system:shutdown", "system:network"
    Custom(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Constraints {
    pub max_calls: Option<u32>,      // Max Anzahl Aufrufe
    pub time_window: Option<TimeWindow>, // "nur zwischen 9-17 Uhr"
    pub max_data_size: Option<u64>,  // "max 10MB"
    pub allowed_args: Option<Vec<String>>, // Erlaubte Argumente
    pub requires_approval: bool,     // Braucht User-Bestätigung
}

pub enum Subject {
    Agent(AgentId),
    Skill(SkillId),
    User(UserId),
    Delegated { from: AgentId, to: AgentId },
}
```

## 2. Capability-Check-Flow

```
Skill fordert Capability an
  ↓
CapabilityStore: Existiert diese Capability?
  ↓
Nein → Ablehnung + Audit-Log
Ja → Prüfen: Abgelaufen? Constraints erfüllt?
  ↓
Constraints verletzt → Ablehnung + Audit-Log
Constraints OK → Capability gültig
  ↓
Skill ausführen
  ↓
Ergebnis + Audit-Log
```

## 3. Capability-Delegation

```rust
// Agent A delegiert Capability an Agent B
pub fn delegate_capability(
    cap: &Capability,
    from: &AgentId,
    to: &AgentId,
    new_constraints: Constraints,
    sign_key: &SigningKey,
) -> Result<Capability, DelegationError> {
    let mut delegated = cap.clone();
    delegated.id = generate_cap_id();
    delegated.subject = Subject::Delegated { from: from.clone(), to: to.clone() };
    delegated.constraints = new_constraints;
    delegated.parent = Some(cap.id);
    delegated.signature = sign(&delegated, sign_key)?;
    Ok(delegated)
}
```

## 4. Sandbox-Stufen

```rust
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum SandboxLevel {
    // Keine Isolation (nur interne, vertrauenswürdige Skills)
    None,

    // Eingeschränkte Syscalls via seccomp/landlock (Rust)
    Restricted {
        allowed_syscalls: Vec<Syscall>,
        allowed_paths: Vec<PathPattern>,
        network: NetworkPolicy,
    },

    // gVisor: Volle OS-Isolation
    Gvisor {
        image: String,
        memory_limit: u64,
        cpu_limit: f32,
        network_policy: NetworkPolicy,
    },

    // Docker/Podman Container
    Container {
        image: String,
        capabilities: Vec<LinuxCapability>,
        seccomp_profile: String,
        network: NetworkPolicy,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum NetworkPolicy {
    None,                // Kein Netzwerk
    Outbound { domains: Vec<String> },  // Nur bestimmte Domains
    Inbound { ports: Vec<u16> },       // Nur bestimmte Ports
    Full,                // Alles erlaubt
}
```

## 5. Zero-Trust-Regeln

1. **Keine Default-Berechtigungen**: Jeder Skill startet mit Capability = None
2. **Least Privilege**: Capabilities sind minimal, genau passend zur Aufgabe
3. **Zeitliche Begrenzung**: Capabilities verfallen nach definierter Zeit
4. **Rückruf**: Capabilities können vom Issuer widerrufen werden
5. **Audit-Pflicht**: Jede Capability-Nutzung wird protokolliert
6. **Signatur-Pflicht**: Capabilities sind kryptografisch signiert
7. **Approval für Risiko**: Hohe Capabilities erfordern User-Bestätigung

## 6. Approval-Flow

```
Skill benötigt: "shell:exec" mit Args ["rm", "-rf", "/"]
  ↓
Constraints prüfen → requires_approval = true
  ↓
Approval-Request an User senden (via aktuelles Interface)
  ↓
User: "Ja" → Capability temporär erteilen, ausführen
User: "Nein" → Capability verweigern, Skill fehlschlagen
User: "Immer erlauben" → Regel erstellen (dauerhafte Erlaubnis)
```

## 7. Audit-Log

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditEntry {
    pub id: AuditId,
    pub timestamp: i64,
    pub actor: Actor,
    pub action: String,
    pub resource: Resource,
    pub result: AuditResult,
    pub metadata: HashMap<String, JsonValue>,
    pub hash: String,  // Unveränderlich (Teil der Kette)
}

pub enum AuditResult {
    Allowed,
    Denied { reason: String },
    Approved { approver: UserId },
    Delegated { to: AgentId },
}
```

## 8. Integration

```rust
pub struct SecurityContext {
    pub capabilities: CapabilityStore,
    pub audit_log: AuditLog,
    pub signing_key: SigningKey,
    pub verification_key: VerificationKey,
    pub approval_channel: Box<dyn ApprovalChannel>,
}

pub trait CapabilityChecker {
    fn check(&self, required: &[Capability]) -> Result<CapabilityGrant, SecurityError>;
    fn request_approval(&self, cap: &Capability) -> ApprovalRequest;
    fn revoke(&self, cap_id: &CapId) -> Result<(), SecurityError>;
}
```

## 9. Checkliste

- [ ] Capability-Datenmodelle
- [ ] Capability-Store (CRUD)
- [ ] Capability-Prüfung (Check-Logik)
- [ ] Capability-Delegation (mit Signatur)
- [ ] Signatur-Erstellung und -Verifizierung
- [ ] Approval-Flow (User-Interaktion)
- [ ] Sandbox-Stufen (None, Restricted, gVisor, Container)
- [ ] Audit-Log (unveränderlich, verkettet)
- [ ] Constraint-Prüfung (Zeit, Anzahl, Größe)
- [ ] Revocation-Mechanismus
- [ ] Integration in Skill-Execution
- [ ] Unit-Tests für Capability-Prüfung
- [ ] Integration-Test: Delegation zwischen zwei Agenten
