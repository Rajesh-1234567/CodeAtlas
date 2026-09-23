import { Handle, Position } from "@xyflow/react";

function GraphNode({ data }) {
  const node = data.graphNode;

  const nodeColors = {
    FILE: "#2563eb",
    CLASS: "#7c3aed",
    FUNCTION: "#059669",
    METHOD: "#d97706",
    EXTERNAL: "#6b7280",
  };

  const color = nodeColors[node.type] || "#6b7280";

  return (
    <div
      style={{
        minWidth: "160px",
        padding: "10px 14px",
        borderRadius: "8px",
        border: `2px solid ${color}`,
        background: "#ffffff",
        boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
        position: "relative",
      }}
    >
      {/* Incoming edges */}
      <Handle
        type="target"
        position={Position.Top}
      />

      {/* Outgoing edges */}
      <Handle
        type="source"
        position={Position.Bottom}
      />

      <div
        style={{
          fontSize: "12px",
          fontWeight: "bold",
          color,
          marginBottom: "5px",
        }}
      >
        {node.type}
      </div>

      <div
        style={{
          fontSize: "14px",
          fontWeight: "600",
          wordBreak: "break-word",
        }}
      >
        {node.name}
      </div>

      {node.file && (
        <div
          style={{
            marginTop: "5px",
            fontSize: "11px",
            color: "#6b7280",
          }}
        >
          {node.file}
        </div>
      )}
    </div>
  );
}

export default GraphNode;