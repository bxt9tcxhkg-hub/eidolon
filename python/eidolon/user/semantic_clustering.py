"""Semantisches Topic-Clustering mit hybridem Ansatz."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from eidolon.user.semantic_clustering_algorithms import agglomerative_clusters, normalize_dense_vectors
from eidolon.user.semantic_clustering_views import format_topic_clusters
from eidolon.user.semantic_ollama import check_ollama_embeddings, get_ollama_embeddings
from eidolon.user.semantic_utils import TfidfVectorizer, tokenize


class SemanticClusterer:
    """Agglomeratives Hierarchisches Clustering für Texte."""

    def __init__(self, min_similarity: float = 0.35):
        self.min_similarity = min_similarity
        self.vectorizer = TfidfVectorizer()

    def cluster(self, documents: list[str]) -> list[dict[str, Any]]:
        if not documents:
            return []
        tokenized = [tokenize(document) for document in documents]
        vectors = self.vectorizer.fit_transform(tokenized)
        return agglomerative_clusters(vectors, tokenized, self.min_similarity)


class SemanticTopicClusterer:
    """Verwendet Ollama Embeddings wenn verfügbar, sonst TF-IDF."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self._ollama_available: bool | None = None

    def _check_ollama(self) -> bool:
        if self._ollama_available is None:
            self._ollama_available = check_ollama_embeddings()
        return self._ollama_available

    async def _get_ollama_embeddings(self, texts: list[str]) -> list[list[float]] | None:
        if not self._check_ollama():
            return None
        return await get_ollama_embeddings(texts)

    async def cluster_interactions(self, interactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not interactions:
            return []
        texts = [item.get('text', '') for item in interactions]
        tokenized = [tokenize(text) for text in texts]
        ollama_embeddings = await self._get_ollama_embeddings(texts)
        if ollama_embeddings and len(ollama_embeddings) == len(texts):
            clusters = agglomerative_clusters(normalize_dense_vectors(ollama_embeddings), tokenized, 0.5)
            source = 'ollama'
        else:
            clusters = SemanticClusterer(min_similarity=0.3).cluster(texts)
            source = 'tfidf'
        return format_topic_clusters(clusters, interactions, source)


_clusterer: SemanticTopicClusterer | None = None


def get_semantic_clusterer(project_root: Path) -> SemanticTopicClusterer:
    global _clusterer
    if _clusterer is None:
        _clusterer = SemanticTopicClusterer(project_root)
    return _clusterer
