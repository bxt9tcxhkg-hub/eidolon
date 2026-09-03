from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

TOKEN_RE = re.compile(r"[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß0-9_-]{2,}")
STOPWORDS = {
    'und', 'oder', 'aber', 'dass', 'wenn', 'weil', 'nicht', 'noch', 'auch',
    'wieder', 'über', 'eine', 'einen', 'einer', 'einem', 'dieser', 'dieses',
    'diese', 'der', 'die', 'das', 'mit', 'für', 'auf', 'von', 'ist', 'sind',
    'ich', 'wir', 'du', 'er', 'sie', 'es', 'man', 'mir', 'mich', 'mein',
    'dein', 'sein', 'ihr', 'uns', 'euch', 'wie', 'was', 'warum', 'wird',
    'werden', 'haben', 'hast', 'hat', 'schon', 'sehr', 'mehr', 'nur',
}


def tokenize(text: str, stopwords: set[str] | None = None) -> list[str]:
    blocked = stopwords or STOPWORDS
    return [token.lower() for token in TOKEN_RE.findall(text) if token.lower() not in blocked]


class TfidfVectorizer:
    def __init__(self):
        self.vocabulary: dict[str, int] = {}
        self.idf: dict[str, float] = {}

    def fit(self, documents: list[list[str]]) -> 'TfidfVectorizer':
        doc_count = len(documents)
        df: Counter[str] = Counter()
        for doc in documents:
            for term in set(doc):
                df[term] += 1
        self.vocabulary = {}
        self.idf = {}
        for term, count in df.items():
            if count >= 2 or doc_count < 5:
                idx = len(self.vocabulary)
                self.vocabulary[term] = idx
                self.idf[term] = math.log((1 + doc_count) / (1 + count)) + 1
        return self

    def transform(self, documents: list[list[str]]) -> list[dict[int, float]]:
        vectors: list[dict[int, float]] = []
        for doc in documents:
            tf = Counter(doc)
            max_tf = max(tf.values()) if tf else 1
            vec: dict[int, float] = {}
            for term, count in tf.items():
                if term in self.vocabulary:
                    idx = self.vocabulary[term]
                    vec[idx] = (0.5 + 0.5 * (count / max_tf)) * self.idf.get(term, 1.0)
            vectors.append(normalize_sparse_vector(vec))
        return vectors

    def fit_transform(self, documents: list[list[str]]) -> list[dict[int, float]]:
        return self.fit(documents).transform(documents)


def normalize_sparse_vector(vec: dict[int, float]) -> dict[int, float]:
    norm = math.sqrt(sum(value ** 2 for value in vec.values())) or 1.0
    return {key: value / norm for key, value in vec.items()}


def cosine_similarity(vec_a: dict[int, float], vec_b: dict[int, float]) -> float:
    common = set(vec_a.keys()) & set(vec_b.keys())
    return sum(vec_a[key] * vec_b[key] for key in common) if common else 0.0


def average_centroid(doc_ids: list[int], vectors: list[dict[int, float]]) -> dict[int, float]:
    summed: dict[int, float] = {}
    for idx in doc_ids:
        for dim, val in vectors[idx].items():
            summed[dim] = summed.get(dim, 0.0) + val
    count = len(doc_ids) or 1
    return normalize_sparse_vector({dim: val / count for dim, val in summed.items()})


def build_cluster_payload(cluster: dict[str, Any]) -> dict[str, Any]:
    token_freq = Counter(cluster['tokens'])
    top_tokens = [token for token, _ in token_freq.most_common(3)]
    return {
        'label': ' '.join(top_tokens).title() if top_tokens else 'Verschiedenes',
        'doc_indices': cluster['docs'],
        'size': len(cluster['docs']),
        'top_terms': top_tokens,
    }
