from app.analysis.impact_analyzer import ImpactAnalyzer
from app.graph.models import CodeGraph, GraphEdge, GraphNode, GraphStats


def create_test_graph():
    nodes = [
        GraphNode(
            id="api",
            type="FUNCTION",
            name="API",
        ),
        GraphNode(
            id="checkout_controller",
            type="FUNCTION",
            name="CheckoutController.create_order",
        ),
        GraphNode(
            id="checkout_service",
            type="FUNCTION",
            name="CheckoutService.checkout",
        ),
        GraphNode(
            id="payment_service",
            type="FUNCTION",
            name="PaymentService.process_payment",
        ),
        GraphNode(
            id="payment_repository",
            type="FUNCTION",
            name="PaymentRepository.save",
        ),
    ]

    edges = [
        GraphEdge(
            source="api",
            target="checkout_controller",
            type="CALLS",
        ),
        GraphEdge(
            source="checkout_controller",
            target="checkout_service",
            type="CALLS",
        ),
        GraphEdge(
            source="checkout_service",
            target="payment_service",
            type="CALLS",
        ),
        GraphEdge(
            source="payment_service",
            target="payment_repository",
            type="CALLS",
        ),
    ]

    stats = GraphStats(
        nodes=len(nodes),
        edges=len(edges),
        classes=0,
        functions=len(nodes),
        calls=len(edges),
        imports=0,
    )

    return CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=stats,
    )


def test_direct_impact():
    graph = create_test_graph()
    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_impact(
        "payment_service",
        depth=1,
    )

    assert len(result) == 1
    assert result[0]["node"] == "checkout_service"
    assert result[0]["impact"] == "DIRECT"
    assert result[0]["distance"] == 1


def test_indirect_impact():
    graph = create_test_graph()
    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_impact(
        "payment_service",
        depth=3,
    )

    assert len(result) == 3

    assert result[0]["node"] == "checkout_service"
    assert result[0]["distance"] == 1
    assert result[0]["impact"] == "DIRECT"

    assert result[1]["node"] == "checkout_controller"
    assert result[1]["distance"] == 2
    assert result[1]["impact"] == "INDIRECT"

    assert result[2]["node"] == "api"
    assert result[2]["distance"] == 3
    assert result[2]["impact"] == "INDIRECT"


def test_depth_limiting():
    graph = create_test_graph()
    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_impact(
        "payment_service",
        depth=2,
    )

    assert len(result) == 2
    assert result[0]["node"] == "checkout_service"
    assert result[1]["node"] == "checkout_controller"


def test_no_dependents():
    graph = create_test_graph()
    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_impact(
        "api",
        depth=3,
    )

    assert result == []


def test_multiple_dependency_paths():
    graph = create_test_graph()

    graph.edges.append(
        GraphEdge(
            source="api",
            target="payment_service",
            type="CALLS",
        )
    )

    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_impact(
        "payment_service",
        depth=3,
    )

    nodes = [item["node"] for item in result]

    assert nodes.count("api") == 1
    assert nodes[0] == "api" or "api" in nodes


def test_circular_dependency():
    graph = create_test_graph()

    graph.edges.append(
        GraphEdge(
            source="payment_service",
            target="checkout_service",
            type="CALLS",
        )
    )

    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_impact(
        "payment_service",
        depth=3,
    )

    nodes = [item["node"] for item in result]

    assert nodes.count("checkout_service") == 1
    assert len(nodes) <= 3


def test_risk_scoring():
    graph = create_test_graph()
    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_risk_score(
        "payment_service",
        depth=3,
    )

    assert result["risk_score"] == 6
    assert result["risk_level"] == "MEDIUM"


def test_nonexistent_node():
    graph = create_test_graph()
    analyzer = ImpactAnalyzer(graph)

    result = analyzer.get_impact(
        "does_not_exist",
        depth=3,
    )

    assert result == []


def test_deterministic_output():
    graph = create_test_graph()
    analyzer = ImpactAnalyzer(graph)

    result1 = analyzer.get_impact(
        "payment_service",
        depth=3,
    )

    result2 = analyzer.get_impact(
        "payment_service",
        depth=3,
    )

    assert result1 == result2