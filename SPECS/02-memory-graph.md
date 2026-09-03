# SPEC 02: Memory Graph

## Ziel
Ein episodisches, graph-basiertes Gedächtnis, das Beziehungen zwischen Personen, Projekten, Skills und Ereignissen modelliert — statt flacher JSONL- oder SQLite-Speicher.

## 1. Datenmodell

### 1.1 Entities (Knoten im Graphen)

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    pub id: EntityId,
    pub entity_type: EntityType,
    pub name: String,
    pub aliases: Vec<String>,
    pub properties: HashMap<String, JsonValue>,
    pub embedding: Option<Vec<f32>>,
    pub created_at: i64,
    pub last_accessed: i64,
    pub access_count: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EntityType {
    Person,
    Project,
    Skill,
    Tool,
    Concept,
    Event,
    Preference,
    Goal,
    Document,
}
```

### 1.2 Episodes (Ereignisse)

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Episode {
    pub id: EpisodeId,
    pub timestamp: i64,
    pub episode_type: EpisodeType,
    pub title: String,
    pub content: JsonValue,
    pub summary: String,
    pub embedding: Option<Vec<f32>>,
    pub related_entities: Vec<EntityId>,
    pub outcome: Option<Outcome>,
    pub emotional_valence: Option<f32>,  // positiv/negativ (für Präferenzlernen)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum EpisodeType {
    UserMessage,
    AgentResponse,
    TaskExecution,
    SkillUsed(SkillId),
    Observation,
    Reflection,
    Interaction { with: AgentId },
    Error,
    Success,
}
```

### 1.3 Relationships (Kanten)

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Relationship {
    pub id: RelId,
    pub from: EntityId,
    pub to: EntityId,
    pub relation: RelationType,
    pub strength: f32,           // 0.0 = schwach, 1.0 = stark
    pub last_confirmed: i64,
    pub evidence: Vec<EpisodeId>, // Welche Episoden belegen diese Beziehung?
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RelationType {
    // Personen
    Knows,
    WorksWith,
    WorksFor,
    Likes,
    Dislikes,

    // Projekte
    WorksOn,
    Owns,
    DependsOn,
    ContributedTo,

    // Skills
    Uses,
    Created,
    Improved,
    Prefers,

    // Allgemein
    RelatedTo,
    ConflictsWith,
    PartOf,
    LocatedAt,
}
```

## 2. Retrieval-Strategie (Tiered)

```rust
pub enum RetrievalStrategy {
    // Tier 1: Exakter Match
    Direct { entity_id: EntityId },
    DirectByName { name: String },

    // Tier 2: Graph-Walk (1-3 Hops)
    GraphWalk {
        start: EntityId,
        max_hops: u32,
        relation_filter: Option<Vec<RelationType>>,
    },

    // Tier 3: Semantische Suche
    Semantic {
        query: String,
        embedding: Vec<f32>,
        entity_types: Option<Vec<EntityType>>,
        limit: usize,
    },

    // Tier 4: Episodisch (zeitbasiert)
    Episodic {
        time_range: (i64, i64),
        episode_types: Option<Vec<EpisodeType>>,
        limit: usize,
    },

    // Tier 5: Kombiniert (Graph + Semantisch)
    Combined {
        query: String,
        max_hops: u32,
        limit: usize,
    },
}
```

## 3. Learning-Mechanismen

### 3.1 Präferenz-Lernen
```
Beobachtung: User lehnt Vorschlag X ab (3x)
  → Beziehung: User --[Dislikes]--> X
  → Stärke: 0.3 → 0.6 → 0.9
  → Nächste Aufgabe: Vorschlag X vermeiden
```

### 3.2 Beziehungs-Evolution
```
Beobachtung: User erwähnt Person Y im Kontext von Projekt Z
  → Neue Beziehung: Y --[WorksOn]--> Z
  → Stärke: 0.5 (erste Erwähnung)
  → Bei wiederholter Erwähnung: Stärke erhöhen
```

### 3.3 Kontext-Kompression
```
Viele Episoden zu ähnlichem Thema
  → Zusammenfassen zu einer "Meta-Episode"
  → Original-Episoden behalten, aber als "archiviert" markieren
  → Meta-Episode verweist auf Originals
```

## 4. Integration mit Agent-Core

```rust
// Memory als Service
pub trait MemoryService: Send + Sync {
    fn store_entity(&self, entity: Entity) -> Result<EntityId>;
    fn store_episode(&self, episode: Episode) -> Result<EpisodeId>;
    fn store_relationship(&self, rel: Relationship) -> Result<RelId>;
    fn retrieve(&self, strategy: RetrievalStrategy) -> Result<Vec<MemoryResult>>;
    fn update_relationship(&self, id: RelId, strength: f32) -> Result<()>;
    fn get_entity_context(&self, entity_id: EntityId) -> Result<EntityContext>;
}
```

## 5. Tech-Stack

| Komponente | Technologie |
|---|---|
| Datenbank | SurrealDB (embedded) |
| Embeddings | candle (Rust, lokale Modelle) oder sentence-transformers (Python) |
| Vektor-Suche | SurrealDB built-in |
| Serialisierung | serde_json / bincode |

## 6. Checkliste

- [ ] SurrealDB embedded integration
- [ ] Entity/Episode/Relationship Models
- [ ] CRUD-Operations für alle drei
- [ ] Retrieval-Strategien (alle 5 Tiers)
- [ ] Embedding-Pipeline (Text → Vektor)
- [ ] Beziehungs-Lern-Logik
- [ ] Präferenz-Extraktion
- [ ] Kontext-Kompression
- [ ] Integration in Agent-Core
- [ ] Unit-Tests für alle Retrieval-Strategien
- [ ] Integration-Test: Agent "lernt" einen User-Präferenz
