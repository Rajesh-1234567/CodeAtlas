from typing import List, Tuple

from app.graph.graph_analyzer import GraphAnalyzer
from app.graph.models import CodeGraph, GraphNode
from app.indexing.search_service import SearchResult
from app.models.chat import SourceReference


class ContextBuilder:
    """
    Builds the context that will be provided to the LLM.

    Combines:
    - Relevant code chunks from semantic search
    - Graph relationships for retrieved code
    - Source references for citations
    """

    def __init__(
        self,
        max_results: int = 5,
        max_graph_items: int = 5,
    ):
        """
        Initialize the context builder.

        max_results:
            Maximum number of semantic search results
            included in the context.

        max_graph_items:
            Maximum number of graph nodes included for
            each retrieved code chunk.
        """

        self.max_results = max_results
        self.max_graph_items = max_graph_items

    def build(
        self,
        question: str,
        search_results: List[SearchResult],
        graph: CodeGraph,
    ) -> Tuple[str, List[SourceReference]]:
        """
        Build structured RAG context.

        Returns:
            context:
                Text containing code and graph information.

            sources:
                Source references corresponding to the
                retrieved code chunks.
        """

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        if not search_results:
            return (
                self._build_empty_context(
                    question
                ),
                [],
            )

        analyzer = GraphAnalyzer(graph)

        selected_results = search_results[
            :self.max_results
        ]

        context_parts = []

        context_parts.append(
            f"Repository question:\n{question}"
        )

        context_parts.append(
            "\nRelevant code:"
        )

        sources = []

        for index, result in enumerate(
            selected_results,
            start=1,
        ):
            chunk = result.chunk

            context_parts.append(
                self._format_code_chunk(
                    index,
                    chunk,
                    result.score,
                )
            )

            sources.append(
                SourceReference(
                    file=chunk.file,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    symbol=chunk.symbol,
                )
            )

            graph_context = (
                self._build_graph_context(
                    chunk.node_id,
                    analyzer,
                )
            )

            if graph_context:
                context_parts.append(
                    graph_context
                )

        context = "\n\n".join(
            context_parts
        )

        return context, sources

    def _format_code_chunk(
        self,
        index: int,
        chunk,
        score: float,
    ) -> str:
        """
        Format one retrieved code chunk.
        """

        return (
            f"\n[{index}]\n"
            f"File: {chunk.file}\n"
            f"Lines: {chunk.start_line}-{chunk.end_line}\n"
            f"Symbol: {chunk.symbol}\n"
            f"Similarity: {score:.4f}\n"
            f"Code:\n"
            f"{chunk.code}"
        )

    def _build_graph_context(
        self,
        node_id: str,
        analyzer: GraphAnalyzer,
    ) -> str:
        """
        Build graph context for one code node.
        """

        dependencies = analyzer.get_dependencies(
            node_id
        )

        dependents = analyzer.get_dependents(
            node_id
        )

        dependencies = dependencies[
            :self.max_graph_items
        ]

        dependents = dependents[
            :self.max_graph_items
        ]

        if not dependencies and not dependents:
            return ""

        lines = [
            "Graph relationships:"
        ]

        if dependencies:
            lines.append(
                "Dependencies:"
            )

            for node in dependencies:
                lines.append(
                    self._format_graph_node(
                        node
                    )
                )

        if dependents:
            lines.append(
                "Dependents:"
            )

            for node in dependents:
                lines.append(
                    self._format_graph_node(
                        node
                    )
                )

        return "\n".join(lines)

    def _format_graph_node(
        self,
        node: GraphNode,
    ) -> str:
        """
        Format a graph node for the LLM context.
        """

        location = ""

        if node.file:
            location = f" | File: {node.file}"

        return (
            f"- {node.name}"
            f" [{node.type}]"
            f"{location}"
        )

    def _build_empty_context(
        self,
        question: str,
    ) -> str:
        """
        Build context when semantic search
        returns no results.
        """

        return (
            f"Repository question:\n{question}\n\n"
            "No relevant repository code was found."
        )