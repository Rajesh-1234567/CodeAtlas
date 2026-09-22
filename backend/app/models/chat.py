from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        description="Natural-language question about the repository"
    )


class SourceReference(BaseModel):
    file: str
    start_line: int
    end_line: int
    symbol: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceReference] = Field(
        default_factory=list
    )