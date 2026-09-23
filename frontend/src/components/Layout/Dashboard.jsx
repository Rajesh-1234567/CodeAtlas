import { useMemo, useState } from "react";

import ArchitectureGraph from "../Graph/ArchitectureGraph";
import GraphControls from "../Graph/GraphControls";
import CodeViewer from "../CodeViewer/CodeViewer";
import { searchRepository } from "../../services/api";

function Dashboard({ repositoryId, setRepositoryId }) {
  const [selectedNode, setSelectedNode] = useState(null);

  const [searchQuery, setSearchQuery] = useState("");

  const [searchResults, setSearchResults] = useState([]);

  const [searchLoading, setSearchLoading] = useState(false);

  const [searchError, setSearchError] = useState("");

  const [nodeFilters, setNodeFilters] = useState({
    FILE: true,
    CLASS: true,
    FUNCTION: true,
    METHOD: true,
    EXTERNAL: true,
  });

  const [edgeFilters, setEdgeFilters] = useState({
    CONTAINS: true,
    IMPORTS: true,
    CALLS: true,
    INHERITS: true,
  });

  const selectedFile = useMemo(() => {
    if (!selectedNode) {
      return null;
    }

    return selectedNode.file || null;
  }, [selectedNode]);

  async function handleSearch(event) {
    event.preventDefault();

    if (!repositoryId || !searchQuery.trim()) {
      return;
    }

    try {
      setSearchLoading(true);
      setSearchError("");

      const results = await searchRepository(
        repositoryId,
        searchQuery
      );

      setSearchResults(results.results || results || []);
    } catch (err) {
      setSearchError(err.message);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  }

  function handleSearchResultClick(result) {
    const node = {
      id: result.node_id,
      type: "SEARCH_RESULT",
      name: result.symbol,
      file: result.file,
      start_line: result.start_line,
      end_line: result.end_line,
    };

    setSelectedNode(node);
  }

  return (
    <div className="dashboard">
      {/* Header */}

      <header className="dashboard-header">
        <div>
          <h1>CodeAtlas</h1>
          <span>Architecture Graph</span>
        </div>

        <form
          className="search-box"
          onSubmit={handleSearch}
        >
          <input
            type="text"
            placeholder="Search code..."
            value={searchQuery}
            onChange={(event) =>
              setSearchQuery(event.target.value)
            }
          />

          <button type="submit">
            Search
          </button>
        </form>
      </header>

      {/* Repository bar */}

      <div className="repository-bar">
        <label>
          Repository ID
        </label>

        <input
          type="text"
          placeholder="Enter repository ID"
          value={repositoryId}
          onChange={(event) =>
            setRepositoryId(event.target.value)
          }
        />

        <button
          type="button"
          onClick={() => {
            setSelectedNode(null);
            setSearchResults([]);
          }}
        >
          Load Graph
        </button>
      </div>

      {/* Main dashboard */}

      <div className="dashboard-body">

        {/* Left panel */}

        <aside className="sidebar">

          <h2>Repository Explorer</h2>

          <div className="sidebar-section">
            <h3>Graph Filters</h3>

            <GraphControls
              nodeFilters={nodeFilters}
              setNodeFilters={setNodeFilters}
              edgeFilters={edgeFilters}
              setEdgeFilters={setEdgeFilters}
            />
          </div>

          <div className="sidebar-section">
            <h3>Search Results</h3>

            {searchLoading && (
              <p>Searching...</p>
            )}

            {searchError && (
              <p className="error-text">
                {searchError}
              </p>
            )}

            {!searchLoading &&
              !searchError &&
              searchResults.length === 0 && (
                <p className="muted-text">
                  No search results.
                </p>
              )}

            <div className="search-results">
              {searchResults.map((result, index) => (
                <button
                  key={`${result.node_id || result.symbol}-${index}`}
                  className="search-result"
                  onClick={() =>
                    handleSearchResultClick(result)
                  }
                >
                  <strong>
                    {result.symbol}
                  </strong>

                  <span>
                    {result.file}
                  </span>

                  <small>
                    Lines {result.start_line}-
                    {result.end_line}
                  </small>
                </button>
              ))}
            </div>
          </div>

        </aside>

        {/* Center */}

        <main className="graph-panel">

          <div className="panel-header">
            <h2>Architecture Graph</h2>

            <div className="legend">
              <span>FILE</span>
              <span>CLASS</span>
              <span>FUNCTION</span>
              <span>METHOD</span>
              <span>EXTERNAL</span>
            </div>
          </div>

          <ArchitectureGraph
            repositoryId={repositoryId}
            onNodeSelect={setSelectedNode}
            nodeFilters={nodeFilters}
            edgeFilters={edgeFilters}
          />

        </main>

      </div>

      {/* Bottom panel */}

      <section className="details-panel">

        <div className="selected-node">

          <h2>Selected Node</h2>

          {!selectedNode && (
            <p className="muted-text">
              Click a node in the graph to inspect it.
            </p>
          )}

          {selectedNode && (
            <>
              <div className="detail-row">
                <strong>Name:</strong>
                <span>
                  {selectedNode.name}
                </span>
              </div>

              <div className="detail-row">
                <strong>Type:</strong>
                <span>
                  {selectedNode.type}
                </span>
              </div>

              <div className="detail-row">
                <strong>File:</strong>
                <span>
                  {selectedNode.file || "N/A"}
                </span>
              </div>

              {selectedNode.start_line && (
                <div className="detail-row">
                  <strong>Lines:</strong>
                  <span>
                    {selectedNode.start_line}-
                    {selectedNode.end_line}
                  </span>
                </div>
              )}
            </>
          )}

        </div>

        <div className="dependencies">

          <h2>Dependencies</h2>

          {selectedNode ? (
            <p className="muted-text">
              Dependency information will be connected
              to the existing graph APIs.
            </p>
          ) : (
            <p className="muted-text">
              Select a node to view dependencies.
            </p>
          )}

        </div>

        <div className="chat-placeholder">

          <button type="button">
            Ask CodeAtlas
          </button>

        </div>

      </section>

      {/* Code viewer */}

      <section className="code-section">

        <h2>Source Code</h2>

        <CodeViewer
          repositoryId={repositoryId}
          filePath={selectedFile}
        />

      </section>

    </div>
  );
}

export default Dashboard;