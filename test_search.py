from app.parser.python_parser import PythonParser
from app.indexing.code_chunker import CodeChunker
from app.indexing.search_service import SearchService


file_path = "backend/app/services/parser_service.py"

# Parse the Python file
parser = PythonParser()
code_file = parser.parse_file(file_path)

# Convert code into chunks
chunker = CodeChunker()
chunks = chunker.chunk_file(code_file)

print("Chunks created:", len(chunks))

# Build semantic search index
search_service = SearchService()
search_service.build_index(chunks)

# Search
query = "Where is repository parsing handled?"

results = search_service.search(
    query=query,
    top_k=3,
)

print("\nQUERY:", query)
print("=" * 60)

for result in results:
    chunk = result.chunk

    print("SYMBOL:", chunk.symbol)
    print("FILE:", chunk.file)
    print("LINES:", chunk.start_line, "-", chunk.end_line)
    print("SCORE:", result.score)
    print("NODE ID:", chunk.node_id)
    print("-" * 60)