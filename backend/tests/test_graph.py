from pathlib import Path

from app.graph.graph_service import GraphService
from app.services.parser_service import ParserService


FIXTURE_PATH = Path("tests/fixtures/graph_project")


def build_test_graph():
    """
    Parse the fixture project and build its code graph.
    """

    parser = ParserService()

    code_structure = parser.parse_repository(
        str(FIXTURE_PATH)
    )

    graph_service = GraphService()

    return graph_service.build_graph(
        str(FIXTURE_PATH),
        code_structure,
    )


def test_file_contains_class():
    """
    A file should contain its classes.
    """

    graph = build_test_graph()

    assert any(
        edge.source == "file:payment.py"
        and edge.target == "class:payment.py:PaymentService"
        and edge.type == "CONTAINS"
        for edge in graph.edges
    )


def test_class_contains_method():
    """
    A class should contain its methods.
    """

    graph = build_test_graph()

    assert any(
        edge.source
        == "class:payment.py:PaymentService"
        and edge.target
        == "method:payment.py:PaymentService.process_payment"
        and edge.type == "CONTAINS"
        for edge in graph.edges
    )


def test_inheritance_relationship():
    """
    A child class should inherit from its parent class.
    """

    graph = build_test_graph()

    assert any(
        edge.source
        == "class:payment.py:PaymentService"
        and edge.target
        == "class:base.py:BaseService"
        and edge.type == "INHERITS"
        for edge in graph.edges
    )


def test_local_function_call():
    """
    A local function call should resolve to the
    correct function.
    """

    graph = build_test_graph()

    assert any(
        edge.source
        == "method:payment.py:PaymentService.process_payment"
        and edge.target
        == "function:payment.py:validate_payment"
        and edge.type == "CALLS"
        for edge in graph.edges
    )


def test_import_relationship():
    """
    Files should have IMPORTS relationships
    for their imported modules.
    """

    graph = build_test_graph()

    assert any(
        edge.source == "file:payment.py"
        and edge.target == "external:base.BaseService"
        and edge.type == "IMPORTS"
        for edge in graph.edges
    )


def test_unresolved_call_becomes_external():
    """
    Calls that cannot be confidently resolved
    should become EXTERNAL nodes.
    """

    graph = build_test_graph()

    assert any(
        edge.source == "function:main.py:main"
        and edge.target == "external:repository.save"
        and edge.type == "CALLS"
        for edge in graph.edges
    )


def test_deterministic_ids():
    """
    Building the graph twice should produce
    the same node and edge IDs.
    """

    graph1 = build_test_graph()
    graph2 = build_test_graph()

    node_ids_1 = {node.id for node in graph1.nodes}
    node_ids_2 = {node.id for node in graph2.nodes}

    edge_ids_1 = {
        (edge.source, edge.target, edge.type)
        for edge in graph1.edges
    }

    edge_ids_2 = {
        (edge.source, edge.target, edge.type)
        for edge in graph2.edges
    }

    assert node_ids_1 == node_ids_2
    assert edge_ids_1 == edge_ids_2