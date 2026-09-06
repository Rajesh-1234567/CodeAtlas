from pathlib import Path

from app.graph.models import GraphNode, GraphEdge
from app.models.code_entities import (
    CodeFile,
    ClassInfo,
    FunctionInfo,
)


class RelationshipResolver:
    """
    Resolves relationships between parsed code entities
    and converts them into graph nodes and edges.
    """

    def __init__(self, repository_root: str):
        self.repository_root = Path(repository_root)

        # Store nodes and edges using deterministic keys.
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[tuple[str, str, str], GraphEdge] = {}

        # Indexes used for resolving local classes/functions.
        self.classes_by_name: dict[str, list[str]] = {}
        self.functions_by_name: dict[str, list[str]] = {}

    def resolve(self, files: list[CodeFile]):
        """
        Resolve all relationships in the repository.
        """

        self._build_symbol_index(files)

        for code_file in files:
            self._add_file_relationships(code_file)

        return list(self.nodes.values()), list(self.edges.values())

    # ---------------------------------------------------------
    # Symbol indexing
    # ---------------------------------------------------------

    def _build_symbol_index(self, files: list[CodeFile]) -> None:
        """
        Build indexes for classes, methods and functions.

        These indexes allow us to resolve obvious local
        inheritance and function-call relationships.
        """

        for code_file in files:
            relative_path = self._relative_path(code_file.path)

            # Index classes and their methods
            for class_info in code_file.classes:
                class_id = self._class_id(
                    relative_path,
                    class_info.name,
                )

                self.classes_by_name.setdefault(
                    class_info.name,
                    [],
                ).append(class_id)

                for method in class_info.methods:
                    method_id = self._method_id(
                        relative_path,
                        class_info.name,
                        method.name,
                    )

                    self.functions_by_name.setdefault(
                        method.name,
                        [],
                    ).append(method_id)

            # Index module-level functions
            for function in code_file.functions:
                function_id = self._function_id(
                    relative_path,
                    function.name,
                )

                self.functions_by_name.setdefault(
                    function.name,
                    [],
                ).append(function_id)

    # ---------------------------------------------------------
    # File relationships
    # ---------------------------------------------------------

    def _add_file_relationships(self, code_file: CodeFile) -> None:
        """
        Add relationships originating from one file.
        """

        relative_path = self._relative_path(code_file.path)

        file_id = self._file_id(relative_path)

        self._add_node(
            GraphNode(
                id=file_id,
                type="FILE",
                name=Path(relative_path).name,
                file=relative_path,
            )
        )

        # File -> Class
        for class_info in code_file.classes:
            self._add_class_relationship(
                relative_path,
                class_info,
            )

        # File -> Function
        for function in code_file.functions:
            self._add_function_relationship(
                relative_path,
                function,
            )

        # File -> Import
        for import_name in code_file.imports:
            self._add_import_relationship(
                file_id,
                import_name,
            )

    # ---------------------------------------------------------
    # Classes
    # ---------------------------------------------------------

    def _add_class_relationship(
        self,
        relative_path: str,
        class_info: ClassInfo,
    ) -> None:
        """
        Add class node and its relationships.
        """

        file_id = self._file_id(relative_path)

        class_id = self._class_id(
            relative_path,
            class_info.name,
        )

        # Add class node
        self._add_node(
            GraphNode(
                id=class_id,
                type="CLASS",
                name=class_info.name,
                file=relative_path,
            )
        )

        # File -> Class
        self._add_edge(
            file_id,
            class_id,
            "CONTAINS",
        )

        # Class -> Parent Class
        for base in class_info.bases:
            parent_id = self._resolve_class(
                base,
                relative_path,
            )

            self._add_edge(
                class_id,
                parent_id,
                "INHERITS",
            )

        # Class -> Method
        for method in class_info.methods:
            method_id = self._method_id(
                relative_path,
                class_info.name,
                method.name,
            )

            # Add method node
            self._add_node(
                GraphNode(
                    id=method_id,
                    type="METHOD",
                    name=method.name,
                    file=relative_path,
                )
            )

            # Class -> Method
            self._add_edge(
                class_id,
                method_id,
                "CONTAINS",
            )

            # Method -> Called entities
            self._add_call_relationships(
                method,
                method_id,
                relative_path,
                class_info.name,
            )

    # ---------------------------------------------------------
    # Functions
    # ---------------------------------------------------------

    def _add_function_relationship(
        self,
        relative_path: str,
        function: FunctionInfo,
    ) -> None:
        """
        Add function node and its relationships.
        """

        function_id = self._function_id(
            relative_path,
            function.name,
        )

        # Add function node
        self._add_node(
            GraphNode(
                id=function_id,
                type="FUNCTION",
                name=function.name,
                file=relative_path,
            )
        )

        file_id = self._file_id(relative_path)

        # File -> Function
        self._add_edge(
            file_id,
            function_id,
            "CONTAINS",
        )

        # Function -> Called entities
        self._add_call_relationships(
            function,
            function_id,
            relative_path,
            None,
        )

    # ---------------------------------------------------------
    # Imports
    # ---------------------------------------------------------

    def _add_import_relationship(
        self,
        file_id: str,
        import_name: str,
    ) -> None:
        """
        Add a file -> external module relationship.
        """

        external_id = self._external_id(import_name)

        self._add_node(
            GraphNode(
                id=external_id,
                type="EXTERNAL",
                name=import_name,
            )
        )

        self._add_edge(
            file_id,
            external_id,
            "IMPORTS",
        )

    # ---------------------------------------------------------
    # Calls
    # ---------------------------------------------------------

    def _add_call_relationships(
        self,
        function: FunctionInfo,
        source_id: str,
        relative_path: str,
        class_name: str | None,
    ) -> None:
        """
        Add CALLS relationships for a function or method.
        """

        for call in function.calls:
            target_id = self._resolve_call(
                call,
                relative_path,
                class_name,
            )

            self._add_edge(
                source_id,
                target_id,
                "CALLS",
            )

    def _resolve_call(
        self,
        call: str,
        relative_path: str,
        class_name: str | None,
    ) -> str:
        """
        Resolve a function call only when the target
        can be identified confidently.

        Otherwise create an EXTERNAL node.
        """

        # -----------------------------------------------------
        # self.method()
        # -----------------------------------------------------

        if call.startswith("self.") and class_name:
            method_name = call.split(".", 1)[1]

            method_id = self._method_id(
                relative_path,
                class_name,
                method_name,
            )

            # Check whether this exact method exists.
            candidates = self.functions_by_name.get(
                method_name,
                [],
            )

            if method_id in candidates:
                return method_id

            return self._external_id(call)

        # -----------------------------------------------------
        # Simple local function call: foo()
        # -----------------------------------------------------

        if "." not in call:
            candidates = self.functions_by_name.get(
                call,
                [],
            )

            # Resolve only when exactly one candidate exists.
            if len(candidates) == 1:
                return candidates[0]

        # -----------------------------------------------------
        # Qualified calls such as:
        #
        # repository.save()
        # stripe.create_payment()
        #
        # remain unresolved because ownership is unknown.
        # -----------------------------------------------------

        return self._external_id(call)

    # ---------------------------------------------------------
    # Class resolution
    # ---------------------------------------------------------

    def _resolve_class(
        self,
        class_name: str,
        relative_path: str,
    ) -> str:
        """
        Resolve a parent class when exactly one class
        with that name exists in the repository.
        """

        candidates = self.classes_by_name.get(
            class_name,
            [],
        )

        if len(candidates) == 1:
            return candidates[0]

        return self._external_id(class_name)

    # ---------------------------------------------------------
    # Path handling
    # ---------------------------------------------------------

    def _relative_path(self, path: str) -> str:
        """
        Convert an absolute parser path into a
        repository-relative path.

        This is important for deterministic IDs.
        """

        file_path = Path(path)

        try:
            return file_path.relative_to(
                self.repository_root
            ).as_posix()

        except ValueError:
            return file_path.as_posix()

    # ---------------------------------------------------------
    # Deterministic ID helpers
    # ---------------------------------------------------------

    @staticmethod
    def _file_id(path: str) -> str:
        return f"file:{path}"

    @staticmethod
    def _class_id(
        path: str,
        class_name: str,
    ) -> str:
        return f"class:{path}:{class_name}"

    @staticmethod
    def _method_id(
        path: str,
        class_name: str,
        method_name: str,
    ) -> str:
        return (
            f"method:{path}:"
            f"{class_name}.{method_name}"
        )

    @staticmethod
    def _function_id(
        path: str,
        function_name: str,
    ) -> str:
        return f"function:{path}:{function_name}"

    @staticmethod
    def _external_id(name: str) -> str:
        return f"external:{name}"

    # ---------------------------------------------------------
    # Graph storage
    # ---------------------------------------------------------

    def _add_node(
        self,
        node: GraphNode,
    ) -> None:
        """
        Add a node only once.
        """

        self.nodes[node.id] = node

    def _add_edge(
        self,
        source: str,
        target: str,
        relationship: str,
    ) -> None:
        """
        Add an edge only once.
        """

        edge = GraphEdge(
            source=source,
            target=target,
            type=relationship,
        )

        key = (
            source,
            target,
            relationship,
        )

        self.edges[key] = edge