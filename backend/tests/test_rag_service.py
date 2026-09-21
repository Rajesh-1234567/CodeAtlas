from unittest.mock import Mock

import pytest

from app.ai.context_builder import ContextBuilder
from app.ai.llm_service import LLMService
from app.ai.rag_service import RAGService
from app.graph.models import (
    CodeGraph,
    GraphStats,
)
from app.indexing.search_service import SearchResult
from app.models.chat import SourceReference


def create_test_graph():
    return CodeGraph(
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


def create_mock_search_service():
    search_service = Mock()

    search_service.search.return_value = []

    return search_service


def create_mock_llm():
    generator = Mock(
        return_value=(
            "Payment processing is handled by "
            "PaymentService."
        )
    )

    return LLMService(
        generator=generator
    ), generator


def test_rag_service_returns_answer():
    search_service = create_mock_search_service()
    graph = create_test_graph()

    llm_service, generator = create_mock_llm()

    rag_service = RAGService(
        search_service=search_service,
        graph=graph,
        llm_service=llm_service,
    )

    answer, sources = rag_service.answer(
        "How does payment processing work?"
    )

    assert (
        answer
        == "Payment processing is handled by "
        "PaymentService."
    )

    assert sources == []

    search_service.search.assert_called_once_with(
        query="How does payment processing work?",
        top_k=5,
    )

    generator.assert_called_once()


def test_top_k_is_passed_to_search():
    search_service = create_mock_search_service()
    graph = create_test_graph()

    llm_service, _ = create_mock_llm()

    rag_service = RAGService(
        search_service=search_service,
        graph=graph,
        llm_service=llm_service,
        top_k=3,
    )

    rag_service.answer(
        "Where is authentication handled?"
    )

    search_service.search.assert_called_once_with(
        query="Where is authentication handled?",
        top_k=3,
    )


def test_prompt_contains_question_and_repository_context():
    search_service = create_mock_search_service()
    graph = create_test_graph()

    llm_service, generator = create_mock_llm()

    context_builder = Mock(
        spec=ContextBuilder
    )

    context_builder.build.return_value = (
        "File: payment/service.py\n"
        "Lines: 20-48\n"
        "Code:\n"
        "def process_payment():",
        [
            SourceReference(
                file="payment/service.py",
                start_line=20,
                end_line=48,
                symbol="process_payment",
            )
        ],
    )

    rag_service = RAGService(
        search_service=search_service,
        graph=graph,
        llm_service=llm_service,
        context_builder=context_builder,
    )

    answer, sources = rag_service.answer(
        "What does process_payment do?"
    )

    prompt = generator.call_args[0][0]

    assert "What does process_payment do?" in prompt
    assert "payment/service.py" in prompt
    assert "Lines: 20-48" in prompt
    assert "def process_payment()" in prompt

    assert len(sources) == 1
    assert sources[0].file == "payment/service.py"


def test_empty_question_is_rejected():
    search_service = create_mock_search_service()
    graph = create_test_graph()

    llm_service, _ = create_mock_llm()

    rag_service = RAGService(
        search_service=search_service,
        graph=graph,
        llm_service=llm_service,
    )

    with pytest.raises(ValueError):
        rag_service.answer("")


def test_empty_llm_answer_is_rejected():
    search_service = create_mock_search_service()
    graph = create_test_graph()

    generator = Mock(
        return_value=""
    )

    llm_service = LLMService(
        generator=generator
    )

    rag_service = RAGService(
        search_service=search_service,
        graph=graph,
        llm_service=llm_service,
    )

    with pytest.raises(RuntimeError):
        rag_service.answer(
            "What does this repository do?"
        )


def test_sources_from_context_builder_are_preserved():
    search_service = create_mock_search_service()
    graph = create_test_graph()

    llm_service, _ = create_mock_llm()

    expected_sources = [
        SourceReference(
            file="payment/service.py",
            start_line=20,
            end_line=48,
            symbol="PaymentService.process_payment",
        ),
        SourceReference(
            file="payment/repository.py",
            start_line=10,
            end_line=31,
            symbol="PaymentRepository.save",
        ),
    ]

    context_builder = Mock(
        spec=ContextBuilder
    )

    context_builder.build.return_value = (
        "Relevant repository context",
        expected_sources,
    )

    rag_service = RAGService(
        search_service=search_service,
        graph=graph,
        llm_service=llm_service,
        context_builder=context_builder,
    )

    _, sources = rag_service.answer(
        "How does payment processing work?"
    )

    assert sources == expected_sources


def test_invalid_top_k_is_rejected():
    search_service = create_mock_search_service()
    graph = create_test_graph()

    llm_service, _ = create_mock_llm()

    with pytest.raises(ValueError):
        RAGService(
            search_service=search_service,
            graph=graph,
            llm_service=llm_service,
            top_k=0,
        )