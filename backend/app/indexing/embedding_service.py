from typing import List

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Service responsible for converting text into embeddings.

    The embedding model is kept behind this interface so that
    it can be replaced later without changing the search system.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(
            model_name
        )

    def embed(
        self,
        text: str
    ) -> List[float]:
        """
        Generate an embedding for a single piece of text.
        """

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
        )

        return embedding.tolist()

    def embed_batch(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
        )

        return embeddings.tolist()