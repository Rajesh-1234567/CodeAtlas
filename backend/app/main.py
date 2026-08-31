from fastapi import FastAPI, HTTPException

from app.models.repository import RepositoryRequest, RepositoryResponse
from app.services.repository_service import RepositoryService, RepositoryNotFoundError


app = FastAPI(
    title="CodeAtlas API",
    description="AI-powered codebase intelligence platform",
    version="0.1.0"
)

# Initialize repository service (shared across all requests)
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
async def analyze(request: RepositoryRequest) -> RepositoryResponse:
    """
    Analyze a GitHub repository.
    
    This endpoint:
    1. Validates the GitHub repository URL
    2. Clones the repository
    3. Scans files and detects programming languages
    4. Returns repository metadata
    
    Args:
        request: GitHub repository URL wrapped in RepositoryRequest
        
    Returns:
        RepositoryResponse with analysis results:
        - name: Repository name
        - url: Original GitHub URL
        - total_files: Total file count
        - source_files: Source code file count
        - languages: Programming language breakdown
        
    Raises:
        HTTPException 404: If repository doesn't exist or can't be cloned
        HTTPException 500: If unexpected error occurs
    
    Example:
        Request:
        {
            "url": "https://github.com/octocat/Hello-World"
        }
        
        Response:
        {
            "name": "Hello-World",
            "url": "https://github.com/octocat/Hello-World",
            "total_files": 2,
            "source_files": 1,
            "languages": {
                "Java": 1
            }
        }
    """
    try:
        # Call the repository service to analyze the repository
        result = repository_service.analyze(request.url)
        
        # Return the successful response
        # FastAPI automatically serializes RepositoryResponse to JSON
        return result
    
    except RepositoryNotFoundError as e:
        # Repository doesn't exist or clone failed
        # Raise HTTPException to return HTTP 404 error
        raise HTTPException(
            status_code=404,
            detail=f"Repository analysis failed: {str(e)}"
        )
    
    except Exception as e:
        # Unexpected error during analysis
        # Raise HTTPException to return HTTP 500 error
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )