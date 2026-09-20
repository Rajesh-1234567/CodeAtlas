from app.services.repository_service import RepositoryService


repository_url = "https://github.com/psf/requests"

service = RepositoryService()

print("Analyzing repository...")

try:
    response = service.analyze(repository_url)

    print("\nRepository ID:")
    print(response.repository_id)

    print("\nRepository Name:")
    print(response.name)

    search_service = service.get_search_service(
        response.repository_id
    )

    print("\nChunks indexed:")
    print(len(search_service.chunks))

    query = "Where is the main application logic?"

    results = search_service.search(
        query=query,
        top_k=5
    )

    print("\nQUERY:")
    print(query)

    print("\nSEARCH RESULTS")
    print("=" * 60)

    for result in results:

        chunk = result.chunk

        print("SYMBOL:", chunk.symbol)
        print("FILE:", chunk.file)
        print(
            "LINES:",
            chunk.start_line,
            "-",
            chunk.end_line
        )
        print("SCORE:", result.score)
        print("NODE ID:", chunk.node_id)

        print("-" * 60)

except Exception as error:

    print("\nERROR:")
    print(error)