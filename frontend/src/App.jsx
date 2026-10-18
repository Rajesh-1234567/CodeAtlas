import { useState } from "react";

import ArchitectureGraph from "./components/Graph/ArchitectureGraph";
import GraphControls from "./components/Graph/GraphControls";

const REPOSITORY_ID = "8f335859-dff9-4500-a155-a7cbd16f05d5";

function App() {
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

  const [selectedNode, setSelectedNode] = useState(null);

  function handleNodeFilterChange(type) {
    setNodeFilters((current) => ({
      ...current,
      [type]: !current[type],
    }));
  }

  function handleEdgeFilterChange(type) {
    setEdgeFilters((current) => ({
      ...current,
      [type]: !current[type],
    }));
  }

  return (
    <div className="app">
      <h1>CodeAtlas Architecture Graph</h1>

      <GraphControls
        nodeFilters={nodeFilters}
        edgeFilters={edgeFilters}
        onNodeFilterChange={handleNodeFilterChange}
        onEdgeFilterChange={handleEdgeFilterChange}
      />

      {selectedNode && (
        <div
          style={{
            margin: "15px 0",
            padding: "15px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            background: "#ffffff",
          }}
        >
          <h2>Selected Node</h2>

          <p>
            <strong>Name:</strong> {selectedNode.name}
          </p>

          <p>
            <strong>Type:</strong> {selectedNode.type}
          </p>

          {selectedNode.file && (
            <p>
              <strong>File:</strong> {selectedNode.file}
            </p>
          )}

          {selectedNode.start_line !== undefined &&
            selectedNode.end_line !== undefined && (
              <p>
                <strong>Lines:</strong> {selectedNode.start_line}–
                {selectedNode.end_line}
              </p>
            )}
        </div>
      )}

      <ArchitectureGraph
        repositoryId={REPOSITORY_ID}
        nodeFilters={nodeFilters}
        edgeFilters={edgeFilters}
        onNodeSelect={setSelectedNode}
      />
    </div>
  );
}

export default App;