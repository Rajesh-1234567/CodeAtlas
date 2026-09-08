from collections import deque

from app.graph.models import CodeGraph


class GraphAnalyzer:
    """
    Analyzes the CodeGraph and provides
    dependency and graph traversal operations.
    """

    def __init__(self, graph: CodeGraph):
        self.graph = graph

    def get_dependencies(self, node_id: str):
        """
        Return nodes that the given node directly depends on.

        Dependency relationships:
        - IMPORTS
        - CALLS
        - INHERITS
        """

        dependency_types = {
            "IMPORTS",
            "CALLS",
            "INHERITS",
        }

        dependency_ids = set()

        for edge in self.graph.edges:
            if (
                edge.source == node_id
                and edge.type in dependency_types
            ):
                dependency_ids.add(edge.target)

        return [
            node
            for node in self.graph.nodes
            if node.id in dependency_ids
        ]

    def get_dependents(self, node_id: str):
        """
        Return nodes that directly depend on the given node.

        Looks at the reverse direction of dependency
        relationships.
        """

        dependency_types = {
            "IMPORTS",
            "CALLS",
            "INHERITS",
        }

        dependent_ids = set()

        for edge in self.graph.edges:
            if (
                edge.target == node_id
                and edge.type in dependency_types
            ):
                dependent_ids.add(edge.source)

        return [
            node
            for node in self.graph.nodes
            if node.id in dependent_ids
        ]

    def traverse_dependencies(
        self,
        node_id: str,
        depth: int = 1
    ):
        """
        Traverse dependencies up to the specified depth
        using BFS.
        """

        if depth <= 0:
            return []

        visited = {node_id}
        queue = deque([(node_id, 0)])
        dependency_ids = set()

        dependency_types = {
            "IMPORTS",
            "CALLS",
            "INHERITS",
        }

        while queue:
            current_id, current_depth = queue.popleft()

            if current_depth >= depth:
                continue

            for edge in self.graph.edges:
                if (
                    edge.source == current_id
                    and edge.type in dependency_types
                ):
                    target_id = edge.target

                    if target_id not in visited:
                        visited.add(target_id)
                        dependency_ids.add(target_id)

                        queue.append(
                            (target_id, current_depth + 1)
                        )

        return [
            node
            for node in self.graph.nodes
            if node.id in dependency_ids
        ]

    def shortest_path(
        self,
        from_node: str,
        to_node: str
    ):
        """
        Find the shortest path between two nodes
        using BFS.
        """

        if from_node == to_node:
            return [from_node]

        dependency_types = {
            "IMPORTS",
            "CALLS",
            "INHERITS",
        }

        queue = deque([from_node])
        visited = {from_node}

        parent = {
            from_node: None
        }

        while queue:
            current_id = queue.popleft()

            for edge in self.graph.edges:

                if (
                    edge.source == current_id
                    and edge.type in dependency_types
                ):
                    target_id = edge.target

                    if target_id in visited:
                        continue

                    visited.add(target_id)

                    parent[target_id] = current_id

                    if target_id == to_node:
                        return self._build_path(
                            parent,
                            to_node
                        )

                    queue.append(target_id)

        return []

    def _build_path(
        self,
        parent: dict,
        target: str
    ):
        """
        Reconstruct a path from the parent map.
        """

        path = []

        current = target

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()

        return path

    def find_cycles(self):
        """
        Detect circular dependencies in the graph.
        """

        dependency_types = {
            "IMPORTS",
            "CALLS",
            "INHERITS",
        }

        adjacency = {}

        for node in self.graph.nodes:
            adjacency[node.id] = []

        for edge in self.graph.edges:
            if edge.type in dependency_types:
                adjacency.setdefault(
                    edge.source,
                    []
                ).append(edge.target)

        cycles = []
        visited = set()
        recursion_stack = []
        recursion_set = set()

        def dfs(node_id):
            visited.add(node_id)
            recursion_stack.append(node_id)
            recursion_set.add(node_id)

            for neighbor in adjacency.get(
                node_id,
                []
            ):
                if neighbor not in visited:
                    dfs(neighbor)

                elif neighbor in recursion_set:
                    cycle_start = recursion_stack.index(
                        neighbor
                    )

                    cycle = (
                        recursion_stack[cycle_start:]
                        + [neighbor]
                    )

                    if cycle not in cycles:
                        cycles.append(cycle)

            recursion_stack.pop()
            recursion_set.remove(node_id)

        for node in adjacency:
            if node not in visited:
                dfs(node)

        return cycles

    def get_statistics(self):
        """
        Return graph statistics including cycle count.
        """

        classes = sum(
            1
            for node in self.graph.nodes
            if node.type == "CLASS"
        )

        functions = sum(
            1
            for node in self.graph.nodes
            if node.type in (
                "FUNCTION",
                "METHOD"
            )
        )

        files = sum(
            1
            for node in self.graph.nodes
            if node.type == "FILE"
        )

        calls = sum(
            1
            for edge in self.graph.edges
            if edge.type == "CALLS"
        )

        imports = sum(
            1
            for edge in self.graph.edges
            if edge.type == "IMPORTS"
        )

        cycles = self.find_cycles()

        return {
            "nodes": len(self.graph.nodes),
            "edges": len(self.graph.edges),
            "files": files,
            "classes": classes,
            "functions": functions,
            "calls": calls,
            "imports": imports,
            "cycles": len(cycles),
        }