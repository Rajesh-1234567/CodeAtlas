from unittest.mock import Mock, patch

import pytest

from app.ai.chat_service import ChatService
from app.models.chat import ChatRequest, ChatResponse
from app.services.repository_service import RepositoryNotFoundError


def test_chat_service_returns_chat_response():
    repository_service = Mock()

    search_service = Mock()
    graph = Mock()

    repository_service.get_search_service.return_value = search_service
    repository_service.get_graph.return_value = graph

    chat_service = ChatService(repository_service)

    with patch.object(
        chat_service,
        "_get_llm_service",
        return_value=Mock(),
    ):
        with patch("app.ai.chat_service.RAGService") as rag_class:
            rag_service = rag_class.return_value

            rag_service.answer.return_value = (
                "Payment processing is handled by the payment service.",
                [],
            )

            response = chat_service.chat(
                "repo-123",
                ChatRequest(
                    question="How does payment processing work?"
                ),
            )

    assert isinstance(response, ChatResponse)

    assert response.answer == (
        "Payment processing is handled by the payment service."
    )


def test_chat_service_uses_repository_search_and_graph():
    repository_service = Mock()

    search_service = Mock()
    graph = Mock()

    repository_service.get_search_service.return_value = search_service
    repository_service.get_graph.return_value = graph

    chat_service = ChatService(repository_service)

    with patch.object(
        chat_service,
        "_get_llm_service",
        return_value=Mock(),
    ):
        with patch("app.ai.chat_service.RAGService") as rag_class:
            rag_service = rag_class.return_value

            rag_service.answer.return_value = (
                "Answer",
                [],
            )

            chat_service.chat(
                "repo-123",
                ChatRequest(
                    question="How does payment processing work?"
                ),
            )

            repository_service.get_search_service.assert_called_once_with(
                "repo-123"
            )

            repository_service.get_graph.assert_called_once_with(
                "repo-123"
            )

            rag_class.assert_called_once()


def test_chat_service_rejects_empty_question():
    repository_service = Mock()

    chat_service = ChatService(repository_service)

    with pytest.raises(ValueError):
        chat_service.chat(
            "repo-123",
            ChatRequest(question=""),
        )


def test_chat_service_propagates_repository_not_found():
    repository_service = Mock()

    repository_service.get_search_service.side_effect = (
        RepositoryNotFoundError(
            "Repository not found."
        )
    )

    chat_service = ChatService(repository_service)

    with pytest.raises(RepositoryNotFoundError):
        chat_service.chat(
            "missing-repo",
            ChatRequest(
                question="How does authentication work?"
            ),
        )


def test_chat_service_propagates_llm_failure():
    repository_service = Mock()

    repository_service.get_search_service.return_value = Mock()
    repository_service.get_graph.return_value = Mock()

    chat_service = ChatService(repository_service)

    with patch.object(
        chat_service,
        "_get_llm_service",
        return_value=Mock(),
    ):
        with patch("app.ai.chat_service.RAGService") as rag_class:
            rag_service = rag_class.return_value

            rag_service.answer.side_effect = RuntimeError(
                "LLM service failed."
            )

            with pytest.raises(RuntimeError):
                chat_service.chat(
                    "repo-123",
                    ChatRequest(
                        question="How does authentication work?"
                    ),
                )