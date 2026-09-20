from typing import List, Optional

import numpy as np

from app.indexing.code_chunker import CodeChunk
from app.indexing.embedding_service import EmbeddingService


class SearchResult:
    def __init__(
        self,
        chunk: CodeChunk,
        score: float,
    ):
        self.chunk = chunk
        self.score = score


class SearchService:
    """
    Local semantic search service.

    Stores code chunks and their embeddings in memory
    and retrieves the most semantically similar chunks.
    """

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.chunks: List[CodeChunk] = []
        self.embeddings: List[List[float]] = []

    def build_index(
        self,
        chunks: List[CodeChunk],
    ):
        """
        Build the local vector index from code chunks.
        """

        self.chunks = chunks

        if not chunks:
            self.embeddings = []
            return

        texts = [
            chunk.code
            for chunk in chunks
        ]

        self.embeddings = (
            self.embedding_service.embed_batch(texts)
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        file: Optional[str] = None,
        symbol: Optional[str] = None,
        class_name: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Search for semantically similar code chunks.

        Optional metadata filters:
        - file
        - symbol
        - class_name
        - language
        """

        if not self.chunks:
            return []

        if not query.strip():
            return []

        query_embedding = (
            self.embedding_service.embed(query)
        )

        query_vector = np.array(
            query_embedding
        )

        results = []

        for chunk, embedding in zip(
            self.chunks,
            self.embeddings,
        ):

            # -----------------------------
            # Metadata filters
            # -----------------------------

            if file is not None:
                if file not in chunk.file:
                    continue

            if symbol is not None:
                if symbol.lower() not in chunk.symbol.lower():
                    continue

            if class_name is not None:
                if chunk.class_name is None:
                    continue

                if (
                    chunk.class_name.lower()
                    != class_name.lower()
                ):
                    continue

            if language is not None:
                # Currently CodeAtlas parses Python code.
                if language.lower() != "python":
                    continue

            # -----------------------------
            # Semantic similarity
            # -----------------------------

            chunk_vector = np.array(
                embedding
            )

            score = self._cosine_similarity(
                query_vector,
                chunk_vector,
            )

            results.append(
                SearchResult(
                    chunk=chunk,
                    score=float(score),
                )
            )

        # Highest similarity first
        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]

    def _cosine_similarity(
        self,
        vector_a: np.ndarray,
        vector_b: np.ndarray,
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        """

        denominator = (
            np.linalg.norm(vector_a)
            * np.linalg.norm(vector_b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(vector_a, vector_b)
            / denominator
        )