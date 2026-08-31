import os
import shutil
import uuid
import tempfile
from git import Repo
from git.exc import GitCommandError

from app.models.repository import RepositoryResponse
from app.utils.file_scanner import FileScanner


class RepositoryNotFoundError(Exception):
    """Raised when a repository cannot be cloned or doesn't exist."""
    pass


class RepositoryService:
    """
    Orchestrates the repository analysis pipeline.
    """

    def __init__(self):
        """Initialize the repository service."""
        self.file_scanner = FileScanner()

    def analyze(self, url: str) -> RepositoryResponse:
        """
        Analyze a GitHub repository.
        """
        url = str(url)

        repo_name = self._extract_repo_name(url)
        local_path = self._generate_temp_path(repo_name)

        try:
            self._clone_repository(url, local_path)

            scan_result = self._scan_repository(local_path)

            response = RepositoryResponse(
                name=repo_name,
                url=url,
                total_files=scan_result.total_files,
                source_files=scan_result.source_files,
                languages=scan_result.languages
            )

            return response

        finally:
            self._cleanup(local_path)
    
    def _extract_repo_name(self, url: str) -> str:
        """
        Extract repository name from GitHub URL.
        
        Args:
            url: GitHub URL (e.g., "https://github.com/octocat/Hello-World")
        
        Returns:
            Repository name (e.g., "Hello-World")
        
        Example:
            "https://github.com/facebook/react" → "react"
            "https://github.com/octocat/Hello-World" → "Hello-World"
        """
        # Split URL by '/'
        parts = url.rstrip('/').split('/')
        
        # Repository name is the last part
        repo_name = parts[-1]
        
        return repo_name
    
    def _generate_temp_path(self, repo_name: str) -> str:
        """
        Generate a unique temporary directory path for cloning.
        
        Args:
            repo_name: Name of the repository
        
        Returns:
            Path to temporary directory (does not create it yet)
        
        Example:
            "Hello-World" → "/tmp/codeatlas/hello-world-a1b2c3d4/"
            or on Windows: "C:\\Users\\...\\AppData\\Local\\Temp\\codeatlas\\hello-world-a1b2c3d4\\"
        """
        # Generate unique ID to avoid collisions
        unique_id = str(uuid.uuid4())[:8]
        
        # Get system temp directory
        system_temp = tempfile.gettempdir()
        
        # Create CodeAtlas temp directory path
        codeatlas_temp = os.path.join(system_temp, "codeatlas")
        
        # Create repo-specific path with unique ID
        repo_temp_path = os.path.join(
            codeatlas_temp,
            f"{repo_name.lower()}-{unique_id}"
        )
        
        return repo_temp_path
    
    def _clone_repository(self, url: str, local_path: str) -> None:
        """
        Clone a GitHub repository to the local temporary path.
        
        Args:
            url: GitHub repository URL
            local_path: Local path where to clone
        
        Raises:
            RepositoryNotFoundError: If clone fails
        
        Process:
            1. Create parent directories if they don't exist
            2. Use GitPython to clone the repository
            3. Raise RepositoryNotFoundError on failure
        """
        try:
            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(local_path)
            os.makedirs(parent_dir, exist_ok=True)
            
            # Clone the repository using GitPython
            Repo.clone_from(url, local_path)
        
        except GitCommandError as e:
            # Git clone failed (repo doesn't exist, network error, etc.)
            raise RepositoryNotFoundError(
                f"Failed to clone repository {url}: {str(e)}"
            )
        
        except OSError as e:
            # File system error (no disk space, permission denied, etc.)
            raise RepositoryNotFoundError(
                f"File system error while cloning: {str(e)}"
            )
        
        except Exception as e:
            # Unexpected error
            raise RepositoryNotFoundError(
                f"Unexpected error while cloning: {str(e)}"
            )
    
    def _scan_repository(self, local_path: str) -> object:
        """
        Scan the cloned repository for files and languages.
        
        Args:
            local_path: Path to the cloned repository
        
        Returns:
            ScanResult object with file counts and language breakdown
        
        Raises:
            RepositoryNotFoundError: If scan fails
        
        Process:
            1. Create FileScanner instance
            2. Call scanner.scan() on the repository
            3. Return the ScanResult
        """
        try:
            # Scan the repository
            scan_result = self.file_scanner.scan(local_path)
            
            return scan_result
        
        except Exception as e:
            # Any error during scanning
            raise RepositoryNotFoundError(
                f"Failed to scan repository: {str(e)}"
            )
    
    def _cleanup(self, local_path: str) -> None:
        """
        Delete the temporary directory and cloned repository.
        
        Args:
            local_path: Path to the temporary directory to delete
        
        Note:
            This method is called in a finally block, so it always runs.
            Errors during cleanup are logged but don't fail the request.
        
        Process:
            1. Check if directory exists
            2. Recursively delete directory and contents
            3. Log any errors that occur
        """
        try:
            # Check if path exists before attempting deletion
            if os.path.exists(local_path):
                # Recursively delete the directory and all contents
                shutil.rmtree(local_path)
        
        except Exception as e:
            # Log error but don't raise (cleanup shouldn't fail the request)
            print(f"Warning: Failed to cleanup temporary directory {local_path}: {str(e)}")