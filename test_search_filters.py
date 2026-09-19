from app.services.repository_service import RepositoryService


repository_url = "https://github.com/psf/requests"

service = RepositoryService()

print("Analyzing repository...")

response = service.analyze(repository_url)

repository_id = response.repository_id

search_service = service.get_search_service(
    repository_id
)

print("\nChunks indexed:")
print(len(search_service.chunks))


# -----------------------------------------
# Test 1: Normal semantic search
# -----------------------------------------

print("\nTEST 1: Normal search")
print("=" * 60)

results = search_service.search(
    query="authentication",
    top_k=3
)

for result in results:

    print(
        result.chunk.symbol,
        "|",
        result.score
    )


# -----------------------------------------
# Test 2: Class filter
# -----------------------------------------

print("\nTEST 2: Class filter")
print("=" * 60)

results = search_service.search(
    query="authentication",
    top_k=3,
    class_name="HTTPDigestAuth"
)

for result in results:

    print(
        result.chunk.symbol,
        "|",
        result.score
    )


# -----------------------------------------
# Test 3: File filter
# -----------------------------------------

print("\nTEST 3: File filter")
print("=" * 60)

results = search_service.search(
    query="authentication",
    top_k=3,
    file="auth.py"
)

for result in results:

    print(
        result.chunk.symbol,
        "|",
        result.score
    )