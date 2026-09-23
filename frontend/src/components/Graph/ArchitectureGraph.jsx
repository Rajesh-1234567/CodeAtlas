import { useEffect, useMemo, useState } from "react";

import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { getRepositoryGraph } from "../../services/api";
import GraphNode from "./GraphNode";

const nodeTypes = {
  custom: GraphNode,
};

function ArchitectureGraph({
  repositoryId,
  onNodeSelect,
  nodeFilters,
  edgeFilters,
}) {
  const [graph, setGraph] = useState({
    nodes: [],
    edges: [],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!repositoryId) {
      setGraph({
        nodes: [],
        edges: [],
      });

      setError("");
      return;
    }

    async function loadGraph() {
      try {
        setLoading(true);
        setError("");

        const data = await getRepositoryGraph(repositoryId);

        setGraph({
          nodes: data.nodes || [],
          edges: data.edges || [],
        });
      } catch (err) {
        setError(err.message);
        setGraph({
          nodes: [],
          edges: [],
        });
      } finally {
        setLoading(false);
      }
    }

    loadGraph();
  }, [repositoryId]);

  const visibleNodes = useMemo(() => {
    return graph.nodes.filter((node) => {
      return nodeFilters[node.type] !== false;
    });
  }, [graph.nodes, nodeFilters]);

  const visibleNodeIds = useMemo(() => {
    return new Set(visibleNodes.map((node) => node.id));
  }, [visibleNodes]);

  const nodes = useMemo(() => {
    return visibleNodes.map((node, index) => ({
      id: node.id,

      type: "custom",

      position: {
        x: (index % 5) * 240,
        y: Math.floor(index / 5) * 150,
      },

      data: {
        graphNode: node,
      },
    }));
  }, [visibleNodes]);

  const edges = useMemo(() => {
    return graph.edges
      .filter((edge) => edgeFilters[edge.type] !== false)
      .filter(
        (edge) =>
          visibleNodeIds.has(edge.source) &&
          visibleNodeIds.has(edge.target)
      )
      .map((edge, index) => ({
        id: `${edge.source}-${edge.target}-${edge.type}-${index}`,

        source: edge.source,

        target: edge.target,

        label: edge.type,

        animated: edge.type === "CALLS",

        data: {
          relationshipType: edge.type,
        },
      }));
  }, [graph.edges, edgeFilters, visibleNodeIds]);

  if (!repositoryId) {
    return (
      <div className="graph-message">
        Enter a repository ID to load the architecture graph.
      </div>
    );
  }

  if (loading) {
    return (
      <div className="graph-message">
        Loading architecture graph...
      </div>
    );
  }

  if (error) {
    return (
      <div className="graph-message graph-error">
        Error loading graph: {error}
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="graph-message">
        No graph data available.
      </div>
    );
  }

  return (
    <div
  className="architecture-graph"
  style={{
    width: "100%",
    height: "75vh",
  }}
>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        onNodeClick={(_, node) => {
          if (onNodeSelect) {
            onNodeSelect(node.data.graphNode);
          }
        }}
      >
        <Background />

        <Controls />

        <MiniMap />
      </ReactFlow>
    </div>
  );
}

export default ArchitectureGraph;