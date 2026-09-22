from typing import List, Tuple

from app.ai.context_builder import ContextBuilder
from app.ai.llm_service import LLMService
from app.graph.models import CodeGraph
from app.indexing.search_service import SearchService
from app.models.chat import SourceReference


class RAGService:
    """
    Orchestrates the Retrieval-Augmented Generation pipeline.

    Pipeline:
        Question
            ↓
        Semantic Search
            ↓
        Context Builder
            ↓
        LLM
            ↓
        Answer + Sources
    """

    def __init__(
        self,
        search_service: SearchService,
        graph: CodeGraph,
        llm_service: LLMService,
        context_builder: ContextBuilder | None = None,
        top_k: int = 5,
    ):
        """
        Initialize the RAG service.

        search_service:
            Performs semantic search over the repository.

        graph:
            Repository code graph used to enrich retrieved
            code with relationships.

        llm_service:
            Generates the final natural-language answer.

        context_builder:
            Converts retrieved code and graph information
            into structured LLM context.

        top_k:
            Maximum number of semantic search results
            retrieved for a question.
        """

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        self.search_service = search_service
        self.graph = graph
        self.llm_service = llm_service

        self.context_builder = (
            context_builder
            if context_builder is not None
            else ContextBuilder(
                max_results=top_k
            )
        )

        self.top_k = top_k

    def answer(
        self,
        question: str,
    ) -> Tuple[str, List[SourceReference]]:
        """
        Answer a repository question using RAG.

        Returns:
            answer:
                LLM-generated repository answer.

            sources:
                Source references used to build the answer.
        """

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        search_results = self.search_service.search(
            query=question,
            top_k=self.top_k,
        )

        context, sources = self.context_builder.build(
            question=question,
            search_results=search_results,
            graph=self.graph,
        )

        prompt = self._build_prompt(
            question=question,
            context=context,
        )

        answer = self.llm_service.generate(
            prompt
        )

        if not answer or not answer.strip():
            raise RuntimeError(
                "LLM returned an empty answer."
            )

        return answer.strip(), sources

    def _build_prompt(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Build the prompt sent to the LLM.

        The instructions force the model to stay grounded
        in the repository context.
        """

        return f"""
You are CodeAtlas, an AI assistant that explains
software repositories.

Answer the user's question using ONLY the repository
context provided below.

Rules:
1. Do not invent files, functions, classes, or relationships.
2. Do not use knowledge that is not present in the context.
3. If the provided context is insufficient, clearly say
   that there is not enough repository context to answer.
4. Keep factual code claims grounded in the provided
   source information.
5. When referring to code, mention the relevant file and
   line range when possible.
6. Explain the code clearly and concisely.

User question:
{question}

Repository context:
{context}

Answer:
""".strip()