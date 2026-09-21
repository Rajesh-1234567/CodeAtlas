from app.ai.context_builder import ContextBuilder
from app.graph.models import (
    CodeGraph,
    GraphEdge,
    GraphNode,
    GraphStats,
)
from app.indexing.code_chunker import CodeChunk
from app.indexing.search_service import SearchResult


def create_test_graph():
    nodes = [
        GraphNode(
            id="function:payment.py:process_payment",
            type="FUNCTION",
            name="process_payment",
            file="payment.py",
        ),
        GraphNode(
            id="function:database.py:save_payment",
            type="FUNCTION",
            name="save_payment",
            file="database.py",
        ),
        GraphNode(
            id="function:checkout.py:checkout",
            type="FUNCTION",
            name="checkout",
            file="checkout.py",
        ),
    ]

    edges = [
        GraphEdge(
            source="function:payment.py:process_payment",
            target="function:database.py:save_payment",
            type="CALLS",
        ),
        GraphEdge(
            source="function:checkout.py:checkout",
            target="function:payment.py:process_payment",
            type="CALLS",
        ),
    ]

    stats = GraphStats(
        nodes=3,
        edges=2,
        classes=0,
        functions=3,
        calls=2,
        imports=0,
    )

    return CodeGraph(
        nodes=nodes,
        edges=edges,
        stats=stats,
    )


def create_test_search_result():
    chunk = CodeChunk(
        chunk_id="chunk-1",
        file="payment.py",
        symbol="process_payment",
        class_name=None,
        function_name="process_payment",
        start_line=20,
        end_line=48,
        code=(
            "def process_payment(payment):\n"
            "    result = save_payment(payment)\n"
            "    return result"
        ),
        node_id="function:payment.py:process_payment",
    )

    return SearchResult(
        chunk=chunk,
        score=0.92,
    )


def test_context_contains_question_and_code():
    builder = ContextBuilder()

    graph = create_test_graph()
    search_result = create_test_search_result()

    context, sources = builder.build(
        question="How does payment processing work?",
        search_results=[search_result],
        graph=graph,
    )

    assert "How does payment processing work?" in context
    assert "payment.py" in context
    assert "process_payment" in context
    assert "save_payment" in context

    assert len(sources) == 1


def test_sources_are_preserved():
    builder = ContextBuilder()

    graph = create_test_graph()
    search_result = create_test_search_result()

    _, sources = builder.build(
        question="What does process_payment do?",
        search_results=[search_result],
        graph=graph,
    )

    source = sources[0]

    assert source.file == "payment.py"
    assert source.start_line == 20
    assert source.end_line == 48
    assert source.symbol == "process_payment"


def test_graph_dependencies_and_dependents_are_included():
    builder = ContextBuilder()

    graph = create_test_graph()
    search_result = create_test_search_result()

    context, _ = builder.build(
        question="What calls process_payment?",
        search_results=[search_result],
        graph=graph,
    )

    assert "save_payment" in context
    assert "checkout" in context


def test_empty_search_results():
    builder = ContextBuilder()

    graph = create_test_graph()

    context, sources = builder.build(
        question="Where is authentication handled?",
        search_results=[],
        graph=graph,
    )

    assert "No relevant repository code was found." in context
    assert sources == []


def test_max_results_is_respected():
    builder = ContextBuilder(max_results=1)

    graph = create_test_graph()

    first_result = create_test_search_result()

    second_chunk = CodeChunk(
        chunk_id="chunk-2",
        file="checkout.py",
        symbol="checkout",
        class_name=None,
        function_name="checkout",
        start_line=10,
        end_line=25,
        code="def checkout():\n    process_payment()",
        node_id="function:checkout.py:checkout",
    )

    second_result = SearchResult(
        chunk=second_chunk,
        score=0.80,
    )

    context, sources = builder.build(
        question="How does checkout work?",
        search_results=[
            first_result,
            second_result,
        ],
        graph=graph,
    )

    assert len(sources) == 1
    assert sources[0].file == "payment.py"
    assert "payment.py" in context