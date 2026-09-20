from typing import Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=50
    )

    file: Optional[str] = None
    symbol: Optional[str] = None
    class_name: Optional[str] = None
    language: Optional[str] = None


class SearchResultResponse(BaseModel):
    file: str
    symbol: str
    start_line: int
    end_line: int
    score: float
    node_id: str