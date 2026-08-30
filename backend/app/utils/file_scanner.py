import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ScanResult:
    """
    Result of scanning a repository.
    
    Attributes:
        total_files: Total number of files in the repository
        source_files: Number of source code files
        languages: Dictionary mapping language names to file counts
    """
    total_files: int
    source_files: int
    languages: dict[str, int]


class FileScanner:
    """
    Scans a cloned repository to gather metadata.
    
    Responsibilities:
    - Count total files
    - Count source code files
    - Detect programming languages
    - Ignore irrelevant directories
    """
    
    # Directories to ignore during scanning
    IGNORE_DIRS = {
        '.git',
        'node_modules',
        'venv',
        '.venv',
        '__pycache__',
        'dist',
        'build',
        'target',
        '.pytest_cache',
        '.egg-info',
        'site-packages',
    }
    
    # Mapping of file extensions to programming languages
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.java': 'Java',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.cpp': 'C++',
        '.cc': 'C++',
        '.cxx': 'C++',
        '.c': 'C',
        '.h': 'C',
        '.hpp': 'C++',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.cs': 'C#',
        '.vb': 'VB.NET',
    }
    
    def scan(self, repo_path: str) -> ScanResult:
        """
        Scan a repository and gather metadata.
        
        Args:
            repo_path: Path to the cloned repository
            
        Returns:
            ScanResult with file counts and language breakdown
        """
        total_files = 0
        source_files = 0
        language_counts = {}
        
        # Walk through all directories in the repository
        for root, dirs, files in os.walk(repo_path):
            # Remove ignored directories from traversal
            # This prevents os.walk from descending into them
            dirs[:] = [d for d in dirs if not self.should_ignore_directory(d)]
            
            # Count files in this directory
            for file in files:
                total_files += 1
                
                # Check if this is a source file
                if self.is_source_file(file):
                    source_files += 1
                    
                    # Detect the programming language
                    language = self.detect_language(file)
                    language_counts[language] = language_counts.get(language, 0) + 1
        
        return ScanResult(
            total_files=total_files,
            source_files=source_files,
            languages=language_counts
        )
    
    def should_ignore_directory(self, dir_name: str) -> bool:
        """
        Check if a directory should be ignored during scanning.
        
        Args:
            dir_name: Name of the directory
            
        Returns:
            True if directory should be ignored, False otherwise
        """
        return dir_name in self.IGNORE_DIRS
    
    def is_source_file(self, filename: str) -> bool:
        """
        Check if a file is a source code file.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file is source code, False otherwise
        """
        # Get file extension
        _, ext = os.path.splitext(filename)
        
        # Check if extension is in language map
        return ext.lower() in self.LANGUAGE_MAP
    
    def detect_language(self, filename: str) -> str:
        """
        Detect the programming language from file extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            Language name, or "Other" if unknown
        """
        # Get file extension
        _, ext = os.path.splitext(filename)
        
        # Return language or "Other" if not found
        return self.LANGUAGE_MAP.get(ext.lower(), "Other")