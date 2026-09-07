from pydantic import BaseModel, field_validator, HttpUrl
from urllib.parse import urlparse

from app.models.code_entities import RepositoryCodeStructure


class RepositoryRequest(BaseModel):
    """
    Validates incoming GitHub repository URLs.

    This model ensures that:
    - The URL is a valid HTTP/HTTPS URL
    - The domain is github.com
    - The URL includes a repository path (owner/repo)
    """

    url: HttpUrl

    @field_validator("url")
    @classmethod
    def validate_github_url(cls, value):
        """
        Validate that the URL belongs to GitHub
        and contains an owner/repository path.
        """

        url_string = str(value)

        parsed = urlparse(url_string)

        # Check domain
        if parsed.netloc != "github.com":
            raise ValueError("URL must be from github.com")

        # Check owner/repository path
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError(
                "URL must include repository path (owner/repo)"
            )

        return value


class RepositoryResponse(BaseModel):
    """
    Response model for repository analysis.

    Contains:
    - Repository ID
    - Repository metadata
    - File statistics
    - Programming language breakdown
    - Parsed code structure
    """

    repository_id: str
    name: str
    url: str
    total_files: int
    source_files: int
    languages: dict[str, int]
    code_structure: RepositoryCodeStructure