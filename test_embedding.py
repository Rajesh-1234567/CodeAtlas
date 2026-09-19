from app.indexing.embedding_service import EmbeddingService


embedding_service = EmbeddingService()

text = "Where is payment validation handled?"

embedding = embedding_service.embed(text)

print("Embedding type:", type(embedding))
print("Embedding length:", len(embedding))
print("First 5 values:", embedding[:5])