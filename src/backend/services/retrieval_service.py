import re
from typing import List
import numpy as np
from ..models import DocumentChunk, RetrievalItem
from .embedding_service import EmbeddingService

class HybridRetrievalService:
    def __init__(
        self,
        chunks: List[DocumentChunk],
        embeddings: np.ndarray,
        embedding_service: EmbeddingService,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        self._chunks = chunks
        self._embeddings = embeddings
        self._embedding_service = embedding_service
        self._vector_weight = vector_weight
        self._keyword_weight = keyword_weight

    def update_index(self, chunks: List[DocumentChunk], embeddings: np.ndarray) -> None:
        self._chunks = chunks
        self._embeddings = embeddings

    def retrieve(self, query: str, top_k: int = 5) -> List[RetrievalItem]:
        if not self._chunks or self._embeddings is None or len(self._embeddings) == 0:
            return []

        query_vector = self._embedding_service.embed_query(query)
        vector_scores = self._compute_cosine_similarity(query_vector, self._embeddings)
        keyword_scores = self._compute_keyword_scores(query)

        final_scores = (
            self._vector_weight * vector_scores + self._keyword_weight * keyword_scores
        )
        top_indices = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for index in top_indices:
            results.append(
                RetrievalItem(
                    chunk=self._chunks[index],
                    score=float(final_scores[index]),
                    vector_score=float(vector_scores[index]),
                    keyword_score=float(keyword_scores[index])
                )
            )
        return results

    def _compute_cosine_similarity(self, vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        dot_product = np.dot(matrix, vector)
        matrix_norm = np.linalg.norm(matrix, axis=1)
        vector_norm = np.linalg.norm(vector)
        return dot_product / (matrix_norm * vector_norm + 1e-10)

    def _compute_keyword_scores(self, query: str) -> np.ndarray:
        keywords = [word for word in re.findall(r"\w+", query.lower()) if len(word) > 1]
        scores = np.zeros(len(self._chunks), dtype=np.float32)
        if not keywords:
            return scores

        for idx, chunk in enumerate(self._chunks):
            content_lower = chunk.content.lower()
            file_lower = chunk.source_file.lower()
            matches = sum(
                1 for word in keywords if word in content_lower or word in file_lower
            )
            scores[idx] = matches / len(keywords)
        return scores
