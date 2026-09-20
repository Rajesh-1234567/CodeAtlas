from fastapi import FastAPI, HTTPException, Query

from app.models.repository import RepositoryRequest, RepositoryResponse
from app.models.search import (
    SearchRequest,
    SearchResultResponse,
)
from app.services.repository_service import (
    RepositoryService,
    RepositoryNotFoundError,
)


app = FastAPI(
    title="CodeAtlas API",
    description="AI-powered codebase intelligence platform",
    version="0.1.0"
)


# Initialize repository service
repository_service = RepositoryService()


@app.get("/")
def root():
    """Root endpoint - returns API information."""

    return {
        "message": "Welcome to CodeAtlas API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint - verifies server is running."""

    return {
        "status": "healthy",
        "message": "CodeAtlas is running"
    }


@app.post(
    "/repositories/analyze",
    response_model=RepositoryResponse,
    summary="Analyze a GitHub repository",
    tags=["repositories"]
)
async def analyze(
    request: RepositoryRequest
) -> RepositoryResponse:
    """
    Analyze a GitHub repository.

    This endpoint:
    1. Validates the GitHub repository URL
    2. Clones the repository
    3. Scans files
    4. Detects programming languages
    5. Parses Python code structure
    6. Creates code chunks
    7. Builds semantic search index
    8. Builds the code graph
    9. Stores the graph and search index
    10. Returns repository analysis
    """

    try:
        result = repository_service.analyze(
            request.url
        )

        return result

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Repository analysis failed: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ---------------------------------------------------------
# Semantic Search Endpoint
# ---------------------------------------------------------


@app.post(
    "/repositories/{repository_id}/search",
    response_model=list[SearchResultResponse],
    summary="Search repository code semantically",
    tags=["search"]
)
async def search_repository(
    repository_id: str,
    request: SearchRequest
):
    """
    Search an analyzed repository using semantic similarity.

    Optional metadata filters:
    - file
    - symbol
    - class_name
    - language

    Each result contains a graph node ID so that
    search results can be connected to graph analysis.
    """

    try:
        search_service = (
            repository_service.get_search_service(
                repository_id
            )
        )

        results = search_service.search(
            query=request.query,
            top_k=request.top_k,
            file=request.file,
            symbol=request.symbol,
            class_name=request.class_name,
            language=request.language,
        )

        return [
            SearchResultResponse(
                file=result.chunk.file,
                symbol=result.chunk.symbol,
                start_line=result.chunk.start_line,
                end_line=result.chunk.end_line,
                score=result.score,
                node_id=result.chunk.node_id,
            )
            for result in results
        ]

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ---------------------------------------------------------
# Graph Endpoint
# ---------------------------------------------------------


@app.get(
    "/repositories/{repository_id}/graph",
    summary="Get repository code graph",
    tags=["repositories"]
)
async def get_repository_graph(
    repository_id: str,
    filter: str = Query(
        default="ALL",
        description="Graph filter: ALL, CLASS, FUNCTION, CALLS, or IMPORTS"
    )
):
    """
    Return the code graph for a previously analyzed repository.

    The graph contains:
    - Nodes
    - Relationships
    - Graph statistics

    Supported filters:
    - ALL
    - CLASS
    - FUNCTION
    - CALLS
    - IMPORTS
    """

    try:
        graph = repository_service.get_graph(
            repository_id
        )

        filtered_graph = repository_service.graph_service.filter_graph(
            graph,
            filter
        )

        return filtered_graph

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ---------------------------------------------------------
# Graph Analysis Endpoints
# ---------------------------------------------------------


@app.get(
    "/repositories/{repository_id}/dependencies"
)
def get_dependencies(
    repository_id: str,
    node_id: str
):
    """
    Get direct dependencies of a node.
    """

    try:
        return repository_service.get_dependencies(
            repository_id,
            node_id
        )

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get(
    "/repositories/{repository_id}/dependents"
)
def get_dependents(
    repository_id: str,
    node_id: str
):
    """
    Get nodes that directly depend on the given node.
    """

    try:
        return repository_service.get_dependents(
            repository_id,
            node_id
        )

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get(
    "/repositories/{repository_id}/dependencies/traverse"
)
def traverse_dependencies(
    repository_id: str,
    node_id: str,
    depth: int = 1
):
    """
    Traverse dependencies up to the given depth.
    """

    try:
        return repository_service.traverse_dependencies(
            repository_id,
            node_id,
            depth
        )

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get(
    "/repositories/{repository_id}/path"
)
def shortest_path(
    repository_id: str,
    from_node: str,
    to_node: str
):
    """
    Find the shortest dependency path between two nodes.
    """

    try:
        return repository_service.shortest_path(
            repository_id,
            from_node,
            to_node
        )

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get(
    "/repositories/{repository_id}/cycles"
)
def find_cycles(
    repository_id: str
):
    """
    Find dependency cycles in the repository graph.
    """

    try:
        return repository_service.find_cycles(
            repository_id
        )

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@app.get(
    "/repositories/{repository_id}/graph/stats"
)
def get_graph_statistics(
    repository_id: str
):
    """
    Return statistics about the repository code graph.
    """

    try:
        return repository_service.get_graph_statistics(
            repository_id
        )

    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
@app.get("/repositories/{repository_id}/impact")
def analyze_impact(
    repository_id: str,
    node_id: str,
    depth: int = 3
):
    try:
        return repository_service.analyze_impact(
            repository_id,
            node_id,
            depth
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )