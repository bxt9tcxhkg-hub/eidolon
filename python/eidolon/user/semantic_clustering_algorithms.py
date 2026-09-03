from __future__ import annotations

import math
from typing import Any

from eidolon.user.semantic_utils import average_centroid, build_cluster_payload, cosine_similarity


def agglomerative_clusters(vectors: list[dict[int, float]], tokenized: list[list[str]], min_similarity: float) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = [
        {'docs': [idx], 'centroid': vec, 'tokens': tokenized[idx]}
        for idx, vec in enumerate(vectors)
    ]
    while len(clusters) > 1:
        best_similarity = -1.0
        best_pair = (-1, -1)
        for left in range(len(clusters)):
            for right in range(left + 1, len(clusters)):
                similarity = cosine_similarity(clusters[left]['centroid'], clusters[right]['centroid'])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_pair = (left, right)
        if best_similarity < min_similarity:
            break
        left, right = best_pair
        merged_docs = clusters[left]['docs'] + clusters[right]['docs']
        merged_tokens = clusters[left]['tokens'] + clusters[right]['tokens']
        clusters[left] = {
            'docs': merged_docs,
            'centroid': average_centroid(merged_docs, vectors),
            'tokens': merged_tokens,
        }
        del clusters[right]
    return [build_cluster_payload(cluster) for cluster in clusters]


def normalize_dense_vectors(vectors: list[list[float]]) -> list[dict[int, float]]:
    normalized: list[dict[int, float]] = []
    for vector in vectors:
        norm = math.sqrt(sum(value ** 2 for value in vector)) or 1.0
        normalized.append({idx: value / norm for idx, value in enumerate(vector)})
    return normalized
