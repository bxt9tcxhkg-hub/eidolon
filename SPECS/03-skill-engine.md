# SPEC 03: Skill Engine

## Ziel
Skills laden, validieren, ausführen, automatisch generieren und kontinuierlich verbessern — voll kompatibel mit dem AgentSkills-Format (OpenClaw/Hermes).

## 1. Skill-Format (AgentSkills-kompatibel)

```
skills/<skill-name>/
├── SKILL.md          # Pflicht: Name, Beschreibung, Wann nutzen, Beispiele
├── scripts/
│   └── main.py       # Pflicht: Haupt-Ausführung
├── schemas/
│   └── input.json    # Optional: JSON-Schema für Eingabe
├── templates/
│   └── output.md     # Optional: Ausgabe-Vorlage
└── tests/
    └── test.py       # Optional: Test-Cases
```

**SKILL.md Format**:
```markdown
---
name: calendar-summarize
version: 1.0.0
description: Summarizes calendar events for a given time range.
triggers:
  - "calendar"
  - "termine"
  - "meetings"
tools:
  - calendar:read
  - summarize
inputs:
  - type: string
    name: range
    description: Time range like "this week" or "next 7 days"
    required: true
---

# Calendar Summarize

## When to use
When the user asks about their calendar, meetings, or appointments.

## How to use
1. Parse the time range
2. Fetch calendar events
3. Summarize and return

## Examples
User: "What's on my calendar this week?"
→ Use this skill with range="this week"
```

## 2. Skill-Registry

```rust
#[derive(Debug, Clone)]
pub struct Skill {
    pub id: SkillId,
    pub name: String,
    pub version: String,
    pub description: String,
    pub triggers: Vec<String>,
    pub required_tools: Vec<ToolRef>,
    pub input_schema: Option<JsonSchema>,
    pub output_template: Option<String>,
    pub script_path: PathBuf,
    pub test_path: Option<PathBuf>,
    pub performance: SkillPerformance,
    pub created_at: i64,
    pub last_used: i64,
    pub use_count: u64,
}

#[derive(Debug, Clone, Default)]
pub struct SkillPerformance {
    pub success_rate: f32,      // 0.0 - 1.0
    pub avg_duration_ms: u32,
    pub avg_cost: f64,
    pub common_failures: Vec<String>,
    pub last_evaluation: i64,
}
```

## 3. Skill-Lifecycle

```
┌─────────────┐
│   LOAD      │  SKILL.md lesen, validieren, Script checken
└──────┬──────┘
       ↓
┌─────────────┐
│   READY     │  Skill ist verfügbar
└──────┬──────┘
       ↓
┌─────────────┐
│ EXECUTING   │  In Sandbox ausführen
└──────┬──────┘
       ↓
┌─────────────┐
│ EVALUATING  │  Ergebnis bewerten
└──────┬──────┘
       ↓
┌─────────────┐
│  LEARNING   │  Performance updaten, ggf. Skill verbessern
└──────┬──────┘
       ↓
┌─────────────┐
│   READY     │  (zurück zu READY)
└─────────────┘
```

## 4. Skill-Ausführung

```rust
pub struct SkillExecutor {
    sandbox: SandboxLevel,
    capability_checker: Arc<CapabilityChecker>,
    timeout: Duration,
}

impl SkillExecutor {
    // Skill mit Capability-Check ausführen
    pub async fn execute(
        &self,
        skill: &Skill,
        input: JsonValue,
        required_caps: Vec<Capability>,
    ) -> Result<SkillOutput, SkillError> {
        // 1. Capabilities prüfen
        self.capability_checker.check(&required_caps)?;

        // 2. Input gegen Schema validieren
        if let Some(schema) = &skill.input_schema {
            schema.validate(&input)?;
        }

        // 3. In Sandbox ausführen
        let result = match self.sandbox {
            SandboxLevel::None => self.execute_direct(&skill, &input).await?,
            SandboxLevel::Restricted => self.execute_restricted(&skill, &input).await?,
            SandboxLevel::Gvisor => self.execute_gvisor(&skill, &input).await?,
            SandboxLevel::Container => self.execute_container(&skill, &input).await?,
        };

        // 4. Ergebnis zurückgeben
        Ok(result)
    }
}
```

## 5. Automatische Skill-Generierung

**Trigger**: Wenn ein Task 2+ Mal ähnlich ausgeführt wird (ähnlicher Prompt + ähnliche Tool-Sequenz)

```
Schritt 1: Pattern-Erkennung
  → Vergleich der letzten N Task-Executions
  → Ähnlichkeit berechnen (Prompt-Embedding + Tool-Sequenz)
  → Wenn Similarity > Threshold → Pattern erkannt

Schritt 2: Extraktion
  → Gemeinsame Schritte identifizieren
  → Parameter extrahieren (was variiert?)
  → Skript-Gerüst erstellen

Schritt 3: Generierung
  → SKILL.md aus Template generieren (LLM-gestützt)
  → Script aus extrahierten Schritten generieren
  → Input-Schema ableiten
  → Output-Template erstellen

Schritt 4: Validierung
  → Test-Run mit Beispiel-Input
  → Ergebnis prüfen
  → Wenn OK → Registrieren
  → Wenn Fehler → An LLM zurückschicken, verbessern

Schritt 5: Verbesserung
  → Bei jedem weiteren Einsatz: Performance tracken
  → Wenn Erfolgsrate < 90% → LLM-gestützte Verbesserung
  → Wenn Erfolgsrate > 95% für 10x → Als "zuverlässig" markieren
```

```rust
pub struct SkillGenerator {
    llm_client: Arc<dyn LlmClient>,
    pattern_detector: Arc<PatternDetector>,
    validator: Arc<SkillValidator>,
}

impl SkillGenerator {
    pub async fn try_generate(&self, task: &Task) -> Result<Option<SkillId>, SkillGenError> {
        // 1. Pattern prüfen
        let pattern = self.pattern_detector.detect(task)?;
        if pattern.similarity < 0.8 {
            return Ok(None);  // Kein wiederholtes Pattern
        }

        // 2. Skill generieren
        let skill_doc = self.llm_client.generate_skill_doc(&pattern).await?;
        let script = self.llm_client.generate_script(&pattern).await?;

        // 3. Validieren
        let temp_skill = Skill::from_generated(skill_doc, script);
        self.validator.validate(&temp_skill).await?;

        // 4. Registrieren
        let skill_id = self.registry.register(temp_skill).await?;

        Ok(Some(skill_id))
    }
}
```

## 6. Skill-Import (OpenClaw/Hermes)

```rust
// OpenClaw Skill importieren
pub async fn import_openclaw_skill(path: &Path) -> Result<SkillId, ImportError> {
    let skill_md = read_file(path.join("SKILL.md")).await?;
    let scripts_dir = path.join("scripts");

    // SKILL.md parsen (kompatibel mit OpenClaw Format)
    let skill = parse_agent_skill(&skill_md, Some(scripts_dir))?;

    // Auf Eidolon-Format mappen
    let mapped = map_to_eidolon(skill)?;

    registry.register(mapped).await
}

// Hermes Skill importieren
pub async fn import_hermes_skill(path: &Path) -> Result<SkillId, ImportError> {
    // Ähnlich, aber Hermes-Format parsen
}
```

## 7. Testing

### Unit-Tests
- [ ] SKILL.md Parser (alle Felder)
- [ ] Input-Schema Validierung
- [ ] Capability-Check bei Skill-Ausführung
- [ ] Pattern-Erkennung (Similarity-Berechnung)
- [ ] Skill-Generierung (LLM-Output → valides SKILL.md)

### Integration-Tests
- [ ] Skill-Lifecycle: Load → Execute → Evaluate → Learn
- [ ] Automatische Generierung: 3x ähnlicher Task → Skill wird erstellt
- [ ] Skill-Import: OpenClaw Skill laden und ausführen
- [ ] Fehlerfall: Skill mit fehlendem Script → saubere Fehlermeldung
