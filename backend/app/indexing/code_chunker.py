import hashlib
from pathlib import Path
from typing import List, Optional

from app.models.code_entities import CodeFile, FunctionInfo


class CodeChunk:
    def __init__(
        self,
        chunk_id: str,
        file: str,
        symbol: str,
        class_name: Optional[str],
        function_name: str,
        start_line: int,
        end_line: int,
        code: str,
        node_id: str,
    ):
        self.chunk_id = chunk_id
        self.file = file
        self.symbol = symbol
        self.class_name = class_name
        self.function_name = function_name
        self.start_line = start_line
        self.end_line = end_line
        self.code = code
        self.node_id = node_id


class CodeChunker:

    def chunk_file(
        self,
        code_file: CodeFile
    ) -> List[CodeChunk]:
        """
        Convert a parsed CodeFile into searchable code chunks.
        """

        chunks = []

        if code_file.status != "ok":
            return chunks

        path = Path(code_file.path)

        try:
            lines = path.read_text(
                encoding="utf-8"
            ).splitlines()

        except (
            OSError,
            UnicodeDecodeError
        ):
            return chunks

        # Top-level functions
        for function in code_file.functions:

            chunk = self._create_function_chunk(
                file_path=code_file.path,
                function=function,
                lines=lines,
                class_name=None,
            )

            chunks.append(chunk)

        # Class methods
        for class_info in code_file.classes:

            for method in class_info.methods:

                chunk = self._create_function_chunk(
                    file_path=code_file.path,
                    function=method,
                    lines=lines,
                    class_name=class_info.name,
                )

                chunks.append(chunk)

        return chunks

    def _create_function_chunk(
        self,
        file_path: str,
        function: FunctionInfo,
        lines: List[str],
        class_name: Optional[str],
    ) -> CodeChunk:
        """
        Create one searchable chunk for a function or method.
        """

        start_line = function.line_start
        end_line = function.line_end

        # Python list indexes start at 0,
        # while source-code line numbers start at 1.
        code = "\n".join(
            lines[start_line - 1:end_line]
        )

        # Normalize Windows paths so that node IDs
        # remain consistent across operating systems.
        normalized_path = file_path.replace(
            "\\",
            "/"
        )

        if class_name:

            symbol = (
                f"{class_name}.{function.name}"
            )

            node_id = (
                f"method:{normalized_path}:"
                f"{class_name}.{function.name}"
            )

        else:

            symbol = function.name

            node_id = (
                f"function:{normalized_path}:"
                f"{function.name}"
            )

        chunk_id = self._generate_chunk_id(
            normalized_path,
            symbol,
            start_line,
            end_line,
        )

        return CodeChunk(
            chunk_id=chunk_id,
            file=normalized_path,
            symbol=symbol,
            class_name=class_name,
            function_name=function.name,
            start_line=start_line,
            end_line=end_line,
            code=code,
            node_id=node_id,
        )

    def _generate_chunk_id(
        self,
        file_path: str,
        symbol: str,
        start_line: int,
        end_line: int,
    ) -> str:
        """
        Generate a deterministic ID for a code chunk.
        """

        value = (
            f"{file_path}:"
            f"{symbol}:"
            f"{start_line}:"
            f"{end_line}"
        )

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()