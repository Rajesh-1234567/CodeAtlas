from app.parser.python_parser import PythonParser
from app.indexing.code_chunker import CodeChunker


file_path = "backend/app/services/parser_service.py"

parser = PythonParser()
code_file = parser.parse_file(file_path)

chunker = CodeChunker()
chunks = chunker.chunk_file(code_file)

for chunk in chunks:
    print("FILE:", chunk.file)
    print("SYMBOL:", chunk.symbol)
    print("START:", chunk.start_line)
    print("END:", chunk.end_line)
    print("NODE ID:", chunk.node_id)
    print("CODE:")
    print(chunk.code)
    print("-" * 50)