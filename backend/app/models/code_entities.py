from typing import List, Optional
from pydantic import BaseModel, Field


class FunctionInfo(BaseModel):
    name: str
    line_start: int
    line_end: int
    parameters: List[str] = Field(default_factory=list)
    calls: List[str] = Field(default_factory=list)


class ClassInfo(BaseModel):
    name: str
    line_start: int
    line_end: int
    bases: List[str] = Field(default_factory=list)
    methods: List[FunctionInfo] = Field(default_factory=list)


class CodeFile(BaseModel):
    path: str
    imports: List[str] = Field(default_factory=list)
    classes: List[ClassInfo] = Field(default_factory=list)
    functions: List[FunctionInfo] = Field(default_factory=list)
    calls: List[str] = Field(default_factory=list)
    status: str = "ok"
    error: Optional[str] = None


class RepositoryCodeStructure(BaseModel):
    files: List[CodeFile] = Field(default_factory=list)


