from typing import Literal

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    type: Literal["FILE", "CLASS", "FUNCTION", "METHOD", "EXTERNAL"]
    name: str
    file: str | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    type: Literal["IMPORTS", "CONTAINS", "CALLS", "INHERITS"]


class GraphStats(BaseModel):
    nodes: int
    edges: int
    classes: int
    functions: int
    calls: int
    imports: int


class CodeGraph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    stats: GraphStats