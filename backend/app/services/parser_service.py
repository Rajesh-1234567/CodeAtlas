from pathlib import Path

from app.models.code_entities import RepositoryCodeStructure
from app.parser.python_parser import PythonParser


class ParserService:

    IGNORE_DIRS = {
        ".git",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
        "dist",
        "build",
        "target",
    }

    def parse_repository(
        self,
        repository_path: str
    ) -> RepositoryCodeStructure:
        """
        Parse all Python files inside a repository.
        """

        repository = Path(
            repository_path
        )

        if not repository.exists():

            raise FileNotFoundError(
                f"Repository does not exist: "
                f"{repository_path}"
            )

        if not repository.is_dir():

            raise NotADirectoryError(
                f"Path is not a directory: "
                f"{repository_path}"
            )

        code_files = []

        for file_path in repository.rglob("*.py"):

            if self.should_ignore(
                file_path,
                repository
            ):
                continue

            parser = PythonParser()

            code_file = parser.parse_file(
                str(file_path)
            )

            code_files.append(
                code_file
            )

        return RepositoryCodeStructure(
            files=code_files
        )

    def should_ignore(
        self,
        file_path: Path,
        repository: Path
    ) -> bool:
        """
        Check whether a file belongs
        to an ignored directory.
        """

        relative_path = file_path.relative_to(
            repository
        )

        for part in relative_path.parts:

            if part in self.IGNORE_DIRS:

                return True

        return False