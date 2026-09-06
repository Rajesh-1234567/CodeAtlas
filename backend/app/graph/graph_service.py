from app.graph.models import CodeGraph, GraphStats
from app.graph.relationship_resolver import RelationshipResolver
from app.models.code_entities import RepositoryCodeStructure


class GraphService:
    """
    Builds a code graph from parsed repository structure.
    """

    def build_graph(
        self,
        repository_root: str,
        code_structure: RepositoryCodeStructure,
    ) -> CodeGraph:

        resolver = RelationshipResolver(repository_root)

        nodes, edges = resolver.resolve(
            code_structure.files
        )

        stats = self._calculate_stats(
            nodes,
            edges
        )

        return CodeGraph(
            nodes=nodes,
            edges=edges,
            stats=stats
        )

    def filter_graph(
        self,
        graph: CodeGraph,
        filter_type: str
    ) -> CodeGraph:

        filter_type = filter_type.upper()

        # Return complete graph
        if filter_type == "ALL":
            return graph

        # Filter CALLS or IMPORTS relationships
        if filter_type in ("CALLS", "IMPORTS"):

            selected_edges = [
                edge
                for edge in graph.edges
                if edge.type == filter_type
            ]

            node_ids = set()

            for edge in selected_edges:
                node_ids.add(edge.source)
                node_ids.add(edge.target)

            selected_nodes = [
                node
                for node in graph.nodes
                if node.id in node_ids
            ]

        # Filter classes
        elif filter_type == "CLASS":

            selected_nodes = [
                node
                for node in graph.nodes
                if node.type == "CLASS"
            ]

            node_ids = {
                node.id
                for node in selected_nodes
            }

            selected_edges = [
                edge
                for edge in graph.edges
                if edge.source in node_ids
                and edge.target in node_ids
            ]

        # Filter functions and methods
        elif filter_type == "FUNCTION":

            selected_nodes = [
                node
                for node in graph.nodes
                if node.type in ("FUNCTION", "METHOD")
            ]

            node_ids = {
                node.id
                for node in selected_nodes
            }

            selected_edges = [
                edge
                for edge in graph.edges
                if edge.source in node_ids
                and edge.target in node_ids
            ]

        else:
            raise ValueError(
                "Invalid graph filter. "
                "Use ALL, CLASS, FUNCTION, CALLS, or IMPORTS."
            )

        stats = self._calculate_stats(
            selected_nodes,
            selected_edges
        )

        return CodeGraph(
            nodes=selected_nodes,
            edges=selected_edges,
            stats=stats
        )

    def _calculate_stats(
        self,
        nodes,
        edges
    ) -> GraphStats:

        classes = sum(
            1
            for node in nodes
            if node.type == "CLASS"
        )

        functions = sum(
            1
            for node in nodes
            if node.type in ("FUNCTION", "METHOD")
        )

        calls = sum(
            1
            for edge in edges
            if edge.type == "CALLS"
        )

        imports = sum(
            1
            for edge in edges
            if edge.type == "IMPORTS"
        )

        return GraphStats(
            nodes=len(nodes),
            edges=len(edges),
            classes=classes,
            functions=functions,
            calls=calls,
            imports=imports
        )