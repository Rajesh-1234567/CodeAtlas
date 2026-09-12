from collections import deque

from app.graph.models import CodeGraph


class ImpactAnalyzer:
    """
    Analyzes the existing CodeGraph to determine
    which nodes may be affected when a node changes.
    """

    DEPENDENCY_TYPES = {"IMPORTS", "CALLS", "INHERITS"}

    def __init__(self, graph: CodeGraph):
        self.graph = graph

    def get_impact(self, node_id: str, depth: int = 1):
        """
        Find all nodes that depend on the target node.

        distance=1 -> DIRECT
        distance>1 -> INDIRECT
        """

        if not self._node_exists(node_id):
            return []

        if depth <= 0:
            return []

        reverse_graph = self._build_reverse_graph()

        visited = {node_id}
        queue = deque([(node_id, 0)])
        impacted = {}

        while queue:
            current_id, current_distance = queue.popleft()

            if current_distance >= depth:
                continue

            for edge in reverse_graph.get(current_id, []):
                dependent_id = edge.source

                if dependent_id in visited:
                    continue

                visited.add(dependent_id)

                distance = current_distance + 1

                impacted[dependent_id] = {
                    "node": dependent_id,
                    "impact": (
                        "DIRECT"
                        if distance == 1
                        else "INDIRECT"
                    ),
                    "reason": self._build_reason(edge),
                    "distance": distance,
                }

                queue.append((dependent_id, distance))

        return sorted(
            impacted.values(),
            key=lambda item: (item["distance"], item["node"])
        )

    def get_risk_score(self, node_id: str, depth: int = 3):
        """
        Calculate a deterministic risk score.

        Direct dependency       +3
        Indirect dependency     +1
        Caller                   +1 each
        Inheritance dependency  +2
        """

        if not self._node_exists(node_id):
            return {
                "risk_score": 0,
                "risk_level": "LOW",
            }

        impacted_nodes = self.get_impact(node_id, depth)

        score = 0

        for item in impacted_nodes:
            if item["impact"] == "DIRECT":
                score += 3
            else:
                score += 1

        # Count direct callers of the target.
        caller_count = sum(
            1
            for edge in self.graph.edges
            if edge.target == node_id
            and edge.type == "CALLS"
        )

        score += caller_count

        # Add extra weight for direct inheritance relationships.
        inheritance_count = sum(
            1
            for edge in self.graph.edges
            if edge.target == node_id
            and edge.type == "INHERITS"
        )

        score += inheritance_count * 2

        return {
            "risk_score": score,
            "risk_level": self._get_risk_level(score),
        }

    def analyze(self, node_id: str, depth: int = 3):
        """
        Return the complete impact analysis.
        """

        if not self._node_exists(node_id):
            return {
                "target": node_id,
                "impacted_nodes": [],
                "risk_score": 0,
                "risk_level": "LOW",
            }

        impacted_nodes = self.get_impact(node_id, depth)
        risk = self.get_risk_score(node_id, depth)

        return {
            "target": node_id,
            "impacted_nodes": impacted_nodes,
            "risk_score": risk["risk_score"],
            "risk_level": risk["risk_level"],
        }

    def _build_reverse_graph(self):
        """
        Reverse the existing dependency relationships.

        Original:
            A -> B

        Reverse:
            B -> A

        This allows us to find who depends on a changed node.
        """

        reverse_graph = {}

        for edge in self.graph.edges:
            if edge.type not in self.DEPENDENCY_TYPES:
                continue

            reverse_graph.setdefault(edge.target, []).append(edge)

        # Sort edges so results are deterministic.
        for node_id in reverse_graph:
            reverse_graph[node_id].sort(
                key=lambda edge: (
                    edge.source,
                    edge.type,
                )
            )

        return reverse_graph

    def _build_reason(self, edge):
        """
        Explain why the dependent node is affected.
        """

        source_name = self._get_node_name(edge.source)
        target_name = self._get_node_name(edge.target)

        if edge.type == "CALLS":
            return f"CALLS {target_name}"

        if edge.type == "IMPORTS":
            return f"IMPORTS {target_name}"

        if edge.type == "INHERITS":
            return f"INHERITS {target_name}"

        return f"{source_name} depends on {target_name}"

    def _get_node_name(self, node_id: str):
        for node in self.graph.nodes:
            if node.id == node_id:
                return node.name

        return node_id

    def _node_exists(self, node_id: str):
        return any(
            node.id == node_id
            for node in self.graph.nodes
        )

    @staticmethod
    def _get_risk_level(score: int):
        if score >= 10:
            return "HIGH"

        if score >= 5:
            return "MEDIUM"

        return "LOW"