from pydantic import BaseModel, field_validator, HttpUrl
from urllib.parse import urlparse


class RepositoryRequest(BaseModel):
    """
    Validates incoming GitHub repository URLs.
    
    This model ensures that:
    - The URL is a valid HTTP/HTTPS URL
    - The domain is github.com
    - The URL includes a repository path (owner/repo)
    """
    url: HttpUrl
    
    @field_validator('url')
    @classmethod
    def validate_github_url(cls, value):
        """
        Custom validation for GitHub URLs.
        
        Args:
            value: The URL to validate (already validated as HttpUrl by Pydantic)
        
        Raises:
            ValueError: If URL is not from GitHub or missing repository path
        """
        # Convert HttpUrl object to string for parsing
        url_string = str(value)
        
        # Parse the URL to extract components
        parsed = urlparse(url_string)
        
        # Check 1: Domain must be github.com
        if parsed.netloc != "github.com":
            raise ValueError("URL must be from github.com")
        
        # Check 2: Path must exist and have owner/repo structure
        # Path looks like: /octocat/Hello-World
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("URL must include repository path (owner/repo)")
        
        return value


class RepositoryResponse(BaseModel):
    """
    Response model for repository analysis.
    
    Contains metadata about a GitHub repository after analysis:
    - Basic info (name, URL)
    - File counts (total and source files)
    - Programming language breakdown
    """
    name: str
    url: str
    total_files: int
    source_files: int
    languages: dict[str, int]