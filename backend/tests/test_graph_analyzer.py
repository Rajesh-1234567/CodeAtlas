from app.graph.models import (
    CodeGraph,
    GraphNode,
    GraphEdge,
    GraphStats,
)

from app.graph.graph_analyzer import GraphAnalyzer


def test_direct_dependencies():

    nodes = [
        GraphNode(
            id="A",
            type="FUNCTION",
            name="A"
        ),
        GraphNode(
            id="B",
            type="FUNCTION",
            name="B"
        ),
        GraphNode(
            id="C",
            type="FUNCTION",
            name="C"
        ),
    ]

    edges = [
        GraphEdge(
            source="A",
            target="B",
            type="CALLS"
        ),
        GraphEdge(
            source="A",
            target="C",
            type="IMPORTS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=3,
            edges=2,
            classes=0,
            functions=3,
            calls=1,
            imports=1,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    dependencies = analyzer.get_dependencies("A")

    dependency_ids = {
        node.id
        for node in dependencies
    }

    assert dependency_ids == {"B", "C"}


def test_direct_dependents():

    nodes = [
        GraphNode(
            id="A",
            type="FUNCTION",
            name="A"
        ),
        GraphNode(
            id="B",
            type="FUNCTION",
            name="B"
        ),
        GraphNode(
            id="C",
            type="FUNCTION",
            name="C"
        ),
    ]

    edges = [
        GraphEdge(
            source="A",
            target="B",
            type="CALLS"
        ),
        GraphEdge(
            source="C",
            target="B",
            type="IMPORTS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=3,
            edges=2,
            classes=0,
            functions=3,
            calls=1,
            imports=1,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    dependents = analyzer.get_dependents("B")

    dependent_ids = {
        node.id
        for node in dependents
    }

    assert dependent_ids == {"A", "C"}


def test_dependency_traversal():

    nodes = [
        GraphNode(
            id="A",
            type="FUNCTION",
            name="A"
        ),
        GraphNode(
            id="B",
            type="FUNCTION",
            name="B"
        ),
        GraphNode(
            id="C",
            type="FUNCTION",
            name="C"
        ),
        GraphNode(
            id="D",
            type="FUNCTION",
            name="D"
        ),
    ]

    edges = [
        GraphEdge(
            source="A",
            target="B",
            type="CALLS"
        ),
        GraphEdge(
            source="B",
            target="C",
            type="CALLS"
        ),
        GraphEdge(
            source="C",
            target="D",
            type="CALLS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=4,
            edges=3,
            classes=0,
            functions=4,
            calls=3,
            imports=0,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    result = analyzer.traverse_dependencies(
        "A",
        depth=2
    )

    result_ids = {
        node.id
        for node in result
    }

    assert result_ids == {"B", "C"}

def test_shortest_path():

    nodes = [
        GraphNode(
            id="A",
            type="FUNCTION",
            name="A"
        ),
        GraphNode(
            id="B",
            type="FUNCTION",
            name="B"
        ),
        GraphNode(
            id="C",
            type="FUNCTION",
            name="C"
        ),
        GraphNode(
            id="D",
            type="FUNCTION",
            name="D"
        ),
    ]

    edges = [
        GraphEdge(
            source="A",
            target="B",
            type="CALLS"
        ),
        GraphEdge(
            source="B",
            target="C",
            type="CALLS"
        ),
        GraphEdge(
            source="C",
            target="D",
            type="CALLS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=4,
            edges=3,
            classes=0,
            functions=4,
            calls=3,
            imports=0,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    path = analyzer.shortest_path("A", "D")

    assert path == ["A", "B", "C", "D"]

def test_shortest_path_no_path():

    nodes = [
        GraphNode(
            id="A",
            type="FUNCTION",
            name="A"
        ),
        GraphNode(
            id="B",
            type="FUNCTION",
            name="B"
        ),
        GraphNode(
            id="C",
            type="FUNCTION",
            name="C"
        ),
    ]

    edges = [
        GraphEdge(
            source="A",
            target="B",
            type="CALLS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=3,
            edges=1,
            classes=0,
            functions=3,
            calls=1,
            imports=0,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    path = analyzer.shortest_path("A", "C")

    assert path == []

def test_find_cycles():

    nodes = [
        GraphNode(
            id="A",
            type="FUNCTION",
            name="A"
        ),
        GraphNode(
            id="B",
            type="FUNCTION",
            name="B"
        ),
        GraphNode(
            id="C",
            type="FUNCTION",
            name="C"
        ),
    ]

    edges = [
        GraphEdge(
            source="A",
            target="B",
            type="CALLS"
        ),
        GraphEdge(
            source="B",
            target="C",
            type="CALLS"
        ),
        GraphEdge(
            source="C",
            target="A",
            type="CALLS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=3,
            edges=3,
            classes=0,
            functions=3,
            calls=3,
            imports=0,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    cycles = analyzer.find_cycles()

    assert cycles == [
        ["A", "B", "C", "A"]
    ]

def test_get_statistics():

    nodes = [
        GraphNode(
            id="file1",
            type="FILE",
            name="file1.py"
        ),
        GraphNode(
            id="class1",
            type="CLASS",
            name="MyClass"
        ),
        GraphNode(
            id="func1",
            type="FUNCTION",
            name="function1"
        ),
        GraphNode(
            id="method1",
            type="METHOD",
            name="method1"
        ),
    ]

    edges = [
        GraphEdge(
            source="file1",
            target="class1",
            type="CONTAINS"
        ),
        GraphEdge(
            source="file1",
            target="func1",
            type="CONTAINS"
        ),
        GraphEdge(
            source="class1",
            target="method1",
            type="CONTAINS"
        ),
        GraphEdge(
            source="func1",
            target="method1",
            type="CALLS"
        ),
        GraphEdge(
            source="file1",
            target="external1",
            type="IMPORTS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=4,
            edges=5,
            classes=1,
            functions=2,
            calls=1,
            imports=1,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    stats = analyzer.get_statistics()

    assert stats["nodes"] == 4
    assert stats["edges"] == 5
    assert stats["files"] == 1
    assert stats["classes"] == 1
    assert stats["functions"] == 2
    assert stats["calls"] == 1
    assert stats["imports"] == 1
    assert stats["cycles"] == 0

def test_nonexistent_node():

    nodes = [
        GraphNode(
            id="A",
            type="FUNCTION",
            name="A"
        ),
        GraphNode(
            id="B",
            type="FUNCTION",
            name="B"
        ),
    ]

    edges = [
        GraphEdge(
            source="A",
            target="B",
            type="CALLS"
        ),
    ]

    graph = CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=GraphStats(
            nodes=2,
            edges=1,
            classes=0,
            functions=2,
            calls=1,
            imports=0,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    dependencies = analyzer.get_dependencies("X")
    dependents = analyzer.get_dependents("X")
    traversal = analyzer.traverse_dependencies("X", depth=2)

    assert dependencies == []
    assert dependents == []
    assert traversal == []

def test_empty_graph():

    graph = CodeGraph(
        nodes=[],
        edges=[],
        stats=GraphStats(
            nodes=0,
            edges=0,
            classes=0,
            functions=0,
            calls=0,
            imports=0,
        ),
    )

    analyzer = GraphAnalyzer(graph)

    assert analyzer.get_dependencies("A") == []
    assert analyzer.get_dependents("A") == []
    assert analyzer.traverse_dependencies("A", depth=2) == []
    assert analyzer.shortest_path("A", "B") == []
    assert analyzer.find_cycles() == []

    stats = analyzer.get_statistics()

    assert stats == {
        "nodes": 0,
        "edges": 0,
        "files": 0,
        "classes": 0,
        "functions": 0,
        "calls": 0,
        "imports": 0,
        "cycles": 0,
    }