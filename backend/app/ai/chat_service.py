from app.ai.rag_service import RAGService
from app.models.chat import ChatRequest, ChatResponse
from app.services.repository_service import (
    RepositoryNotFoundError,
    RepositoryService,
)


class ChatService:
    """
    Application-level service for repository chat.

    Connects a repository to the RAG pipeline and
    returns a structured ChatResponse.
    """

    def __init__(
        self,
        repository_service: RepositoryService,
    ):
        """
        Initialize the chat service.

        repository_service:
            Provides access to the repository's semantic
            search index and code graph.
        """

        self.repository_service = repository_service

    def chat(
        self,
        repository_id: str,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Answer a natural-language question about a repository.
        """

        if not request.question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        search_service = (
            self.repository_service.get_search_service(
                repository_id
            )
        )

        graph = (
            self.repository_service.get_graph(
                repository_id
            )
        )

        rag_service = RAGService(
            search_service=search_service,
            graph=graph,
            llm_service=self._get_llm_service(),
        )

        answer, sources = rag_service.answer(
            request.question
        )

        return ChatResponse(
            answer=answer,
            sources=sources,
        )

    def _get_llm_service(self):
        """
        Return the LLM service used by the RAG pipeline.

        This method is kept separate so the actual provider
        can be configured without changing the chat flow.
        """

        raise NotImplementedError(
            "LLM provider has not been configured yet."
        )