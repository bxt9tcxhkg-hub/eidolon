use sqlx::sqlite::SqlitePool;
use std::path::Path;
use crate::models::*;

pub struct KnowledgeGraph {
    pool: SqlitePool,
}

impl KnowledgeGraph {
    pub async fn new(data_dir: &Path) -> Result<Self, anyhow::Error> {
        std::fs::create_dir_all(data_dir)?;
        let db_path = data_dir.join("knowledge.db");
        let pool = SqlitePool::connect(&format!("sqlite:{}", db_path.display())).await?;

        sqlx::query(
            r#"
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                properties TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            );
            CREATE TABLE IF NOT EXISTS evidence (
                id TEXT PRIMARY KEY,
                claim TEXT NOT NULL,
                status TEXT NOT NULL,
                source TEXT,
                created_at TEXT NOT NULL
            );
            "#,
        )
        .execute(&pool)
        .await?;

        Ok(Self { pool })
    }

    pub async fn add_entity(&self, entity: &Entity) -> Result<(), anyhow::Error> {
        sqlx::query(
            "INSERT OR REPLACE INTO entities (id, entity_type, name, properties, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)"
        )
        .bind(&entity.id)
        .bind(&entity.entity_type)
        .bind(&entity.name)
        .bind(serde_json::to_string(&entity.properties)?)
        .bind(&entity.created_at.to_rfc3339())
        .bind(&entity.updated_at.to_rfc3339())
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    pub async fn add_relationship(&self, rel: &Relationship) -> Result<(), anyhow::Error> {
        sqlx::query(
            "INSERT OR REPLACE INTO relationships (id, source_id, target_id, relationship_type, strength, properties, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        .bind(&rel.id)
        .bind(&rel.source_id)
        .bind(&rel.target_id)
        .bind(&rel.relationship_type)
        .bind(rel.strength)
        .bind(serde_json::to_string(&rel.properties)?)
        .bind(&rel.created_at.to_rfc3339())
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    pub async fn add_evidence(&self, evidence: &Evidence) -> Result<(), anyhow::Error> {
        sqlx::query(
            "INSERT OR REPLACE INTO evidence (id, claim, status, source, created_at) VALUES (?, ?, ?, ?, ?)"
        )
        .bind(&evidence.id)
        .bind(&evidence.claim)
        .bind(format!("{:?}", evidence.status).to_lowercase())
        .bind(&evidence.source)
        .bind(&evidence.created_at.to_rfc3339())
        .execute(&self.pool)
        .await?;
        Ok(())
    }

    pub async fn get_entity(&self, id: &str) -> Result<Option<Entity>, anyhow::Error> {
        let row = sqlx::query_as::<_, EntityRow>("SELECT * FROM entities WHERE id = ?")
            .bind(id)
            .fetch_optional(&self.pool)
            .await?;
        Ok(row.map(|r| r.into()))
    }

    pub async fn get_all_entities(&self) -> Result<Vec<Entity>, anyhow::Error> {
        let rows = sqlx::query_as::<_, EntityRow>("SELECT * FROM entities")
            .fetch_all(&self.pool)
            .await?;
        Ok(rows.into_iter().map(|r| r.into()).collect())
    }

    pub async fn get_all_evidence(&self) -> Result<Vec<Evidence>, anyhow::Error> {
        let rows = sqlx::query_as::<_, EvidenceRow>("SELECT * FROM evidence")
            .fetch_all(&self.pool)
            .await?;
        Ok(rows.into_iter().map(|r| r.into()).collect())
    }

    pub async fn stats(&self) -> Result<GraphStats, anyhow::Error> {
        let entities: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM entities")
            .fetch_one(&self.pool)
            .await?;
        let relationships: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM relationships")
            .fetch_one(&self.pool)
            .await?;
        let evidence: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM evidence")
            .fetch_one(&self.pool)
            .await?;
        Ok(GraphStats {
            entities: entities as usize,
            relationships: relationships as usize,
            evidence: evidence as usize,
        })
    }
}

#[derive(Debug, Clone)]
pub struct Entity {
    pub id: String,
    pub entity_type: String,
    pub name: String,
    pub properties: serde_json::Value,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone)]
pub struct Relationship {
    pub id: String,
    pub source_id: String,
    pub target_id: String,
    pub relationship_type: String,
    pub strength: f64,
    pub properties: serde_json::Value,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct GraphStats {
    pub entities: usize,
    pub relationships: usize,
    pub evidence: usize,
}

#[derive(Debug, sqlx::FromRow)]
struct EntityRow {
    id: String,
    entity_type: String,
    name: String,
    properties: String,
    created_at: String,
    updated_at: String,
}

impl From<EntityRow> for Entity {
    fn from(row: EntityRow) -> Self {
        Self {
            id: row.id,
            entity_type: row.entity_type,
            name: row.name,
            properties: serde_json::from_str(&row.properties).unwrap_or(serde_json::Value::Null),
            created_at: chrono::DateTime::parse_from_rfc3339(&row.created_at)
                .unwrap()
                .with_timezone(&chrono::Utc),
            updated_at: chrono::DateTime::parse_from_rfc3339(&row.updated_at)
                .unwrap()
                .with_timezone(&chrono::Utc),
        }
    }
}

#[derive(Debug, sqlx::FromRow)]
struct EvidenceRow {
    id: String,
    claim: String,
    status: String,
    source: String,
    created_at: String,
}

impl From<EvidenceRow> for Evidence {
    fn from(row: EvidenceRow) -> Self {
        Self {
            id: row.id,
            claim: row.claim,
            status: match row.status.as_str() {
                "verified" => VerificationStatus::Verified,
                "inferred" => VerificationStatus::Inferred,
                "blocked" => VerificationStatus::Blocked,
                _ => VerificationStatus::Unverified,
            },
            source: row.source,
            created_at: chrono::DateTime::parse_from_rfc3339(&row.created_at)
                .unwrap()
                .with_timezone(&chrono::Utc),
        }
    }
}
