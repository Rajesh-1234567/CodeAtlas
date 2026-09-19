import os
import shutil
import uuid
import tempfile

from git import Repo
from git.exc import GitCommandError

from app.graph.graph_analyzer import GraphAnalyzer
from app.models.repository import RepositoryResponse
from app.utils.file_scanner import FileScanner
from app.services.parser_service import ParserService
from app.graph.graph_service import GraphService
from app.graph.models import CodeGraph

from app.indexing.code_chunker import CodeChunker
from app.indexing.search_service import SearchService


class RepositoryNotFoundError(Exception):
    """Raised when a repository cannot be cloned or analyzed."""

    pass


class RepositoryService:
    """
    Orchestrates the repository analysis pipeline.
    """

    def __init__(self):
        """Initialize repository analysis services."""

        self.file_scanner = FileScanner()
        self.parser_service = ParserService()
        self.graph_service = GraphService()
        self.code_chunker = CodeChunker()

        # Store generated graphs in memory.
        # Key = repository ID
        # Value = CodeGraph
        self.graphs: dict[str, CodeGraph] = {}

        # Store semantic search indexes in memory.
        # Key = repository ID
        # Value = SearchService
        self.search_indexes: dict[str, SearchService] = {}

    def analyze(self, url: str) -> RepositoryResponse:
        """
        Analyze a GitHub repository.

        Pipeline:
        1. Extract repository name
        2. Generate temporary directory
        3. Clone repository
        4. Scan repository
        5. Parse Python files
        6. Create code chunks
        7. Build semantic search index
        8. Build code graph
        9. Store graph and search index
        10. Build response
        11. Cleanup temporary directory
        """

        url = str(url)

        repo_name = self._extract_repo_name(url)

        local_path = self._generate_temp_path(repo_name)

        # Generate a unique ID for this analysis
        repository_id = str(uuid.uuid4())

        try:
            # Step 1: Clone repository
            self._clone_repository(
                url,
                local_path
            )

            # Step 2: Scan repository
            scan_result = self._scan_repository(
                local_path
            )

            # Step 3: Parse repository
            code_structure = self._parse_repository(
                local_path
            )

            # Step 4: Create code chunks
            chunks = self._chunk_repository(
                code_structure
            )

            # Step 5: Build semantic search index
            search_service = SearchService()

            search_service.build_index(
                chunks
            )

            self.search_indexes[repository_id] = (
                search_service
            )

            # Step 6: Build code graph
            code_graph = self.graph_service.build_graph(
                repository_root=local_path,
                code_structure=code_structure
            )

            # Step 7: Store graph in memory
            self.graphs[repository_id] = code_graph

            # Step 8: Build final response
            response = RepositoryResponse(
                repository_id=repository_id,
                name=repo_name,
                url=url,
                total_files=scan_result.total_files,
                source_files=scan_result.source_files,
                languages=scan_result.languages,
                code_structure=code_structure
            )

            return response

        finally:
            # Always remove temporary repository
            self._cleanup(local_path)

    # =========================================================
    # Semantic Search
    # =========================================================

    def get_search_service(
        self,
        repository_id: str
    ) -> SearchService:
        """
        Get the semantic search service for a repository.
        """

        if repository_id not in self.search_indexes:
            raise RepositoryNotFoundError(
                f"Repository search index not found: "
                f"{repository_id}"
            )

        return self.search_indexes[
            repository_id
        ]

    def _chunk_repository(
        self,
        code_structure
    ):
        """
        Convert all parsed repository files
        into searchable code chunks.
        """

        all_chunks = []

        for code_file in code_structure.files:

            chunks = self.code_chunker.chunk_file(
                code_file
            )

            all_chunks.extend(chunks)

        return all_chunks

    # =========================================================
    # Graph
    # =========================================================

    def get_graph(
        self,
        repository_id: str
    ) -> CodeGraph:
        """
        Get a previously generated code graph.
        """

        if repository_id not in self.graphs:
            raise RepositoryNotFoundError(
                f"Repository graph not found: {repository_id}"
            )

        return self.graphs[repository_id]

    # =========================================================
    # Graph Analysis
    # =========================================================

    def get_dependencies(
        self,
        repository_id: str,
        node_id: str
    ):
        """
        Get direct dependencies of a node.
        """

        graph = self.get_graph(repository_id)

        analyzer = GraphAnalyzer(graph)

        return analyzer.get_dependencies(node_id)

    def get_dependents(
        self,
        repository_id: str,
        node_id: str
    ):
        """
        Get direct dependents of a node.
        """

        graph = self.get_graph(repository_id)

        analyzer = GraphAnalyzer(graph)

        return analyzer.get_dependents(node_id)

    def traverse_dependencies(
        self,
        repository_id: str,
        node_id: str,
        depth: int = 1
    ):
        """
        Traverse dependencies up to the given depth.
        """

        graph = self.get_graph(repository_id)

        analyzer = GraphAnalyzer(graph)

        return analyzer.traverse_dependencies(
            node_id,
            depth
        )

    def shortest_path(
        self,
        repository_id: str,
        from_node: str,
        to_node: str
    ):
        """
        Find the shortest dependency path
        between two nodes.
        """

        graph = self.get_graph(repository_id)

        analyzer = GraphAnalyzer(graph)

        return analyzer.shortest_path(
            from_node,
            to_node
        )

    def find_cycles(
        self,
        repository_id: str
    ):
        """
        Find all dependency cycles in the graph.
        """

        graph = self.get_graph(repository_id)

        analyzer = GraphAnalyzer(graph)

        return analyzer.find_cycles()

    def get_graph_statistics(
        self,
        repository_id: str
    ):
        """
        Get statistics about the code graph.
        """

        graph = self.get_graph(repository_id)

        analyzer = GraphAnalyzer(graph)

        return analyzer.get_statistics()

    # =========================================================
    # Repository Helpers
    # =========================================================

    def _extract_repo_name(
        self,
        url: str
    ) -> str:
        """
        Extract repository name from GitHub URL.

        Example:
            https://github.com/facebook/react
            -> react
        """

        parts = url.rstrip("/").split("/")

        repo_name = parts[-1]

        return repo_name

    def _generate_temp_path(
        self,
        repo_name: str
    ) -> str:
        """
        Generate a unique temporary directory path.
        """

        # Generate unique ID
        unique_id = str(uuid.uuid4())[:8]

        # Get system temporary directory
        system_temp = tempfile.gettempdir()

        # Create CodeAtlas temporary directory
        codeatlas_temp = os.path.join(
            system_temp,
            "codeatlas"
        )

        # Create repository-specific path
        repo_temp_path = os.path.join(
            codeatlas_temp,
            f"{repo_name.lower()}-{unique_id}"
        )

        return repo_temp_path

    def _clone_repository(
        self,
        url: str,
        local_path: str
    ) -> None:
        """
        Clone a GitHub repository to a temporary directory.
        """

        try:
            # Create parent directory
            parent_dir = os.path.dirname(local_path)

            os.makedirs(
                parent_dir,
                exist_ok=True
            )

            # Clone repository
            Repo.clone_from(
                url,
                local_path
            )

        except GitCommandError as e:

            raise RepositoryNotFoundError(
                f"Failed to clone repository {url}: {str(e)}"
            )

        except OSError as e:

            raise RepositoryNotFoundError(
                f"File system error while cloning: {str(e)}"
            )

        except Exception as e:

            raise RepositoryNotFoundError(
                f"Unexpected error while cloning: {str(e)}"
            )

    def _scan_repository(
        self,
        local_path: str
    ) -> object:
        """
        Scan the cloned repository for files
        and programming languages.
        """

        try:

            scan_result = self.file_scanner.scan(
                local_path
            )

            return scan_result

        except Exception as e:

            raise RepositoryNotFoundError(
                f"Failed to scan repository: {str(e)}"
            )

    def _parse_repository(
        self,
        local_path: str
    ):
        """
        Parse Python files in the cloned repository.
        """

        try:

            code_structure = (
                self.parser_service.parse_repository(
                    local_path
                )
            )

            return code_structure

        except Exception as e:

            raise RepositoryNotFoundError(
                f"Failed to parse repository: {str(e)}"
            )

    def _cleanup(
        self,
        local_path: str
    ) -> None:
        """
        Delete the temporary cloned repository.

        Cleanup errors do not fail the request.
        """

        try:

            if os.path.exists(local_path):

                shutil.rmtree(
                    local_path
                )

        except Exception as e:

            print(
                f"Warning: Failed to cleanup "
                f"temporary directory {local_path}: {str(e)}"
            )