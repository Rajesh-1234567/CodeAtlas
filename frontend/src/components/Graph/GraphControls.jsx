function GraphControls({
  nodeFilters,
  edgeFilters,
  onNodeFilterChange,
  onEdgeFilterChange,
}) {
  const nodeTypes = [
    ["FILE", "FILE"],
    ["CLASS", "CLASS"],
    ["FUNCTION", "FUNCTION"],
    ["METHOD", "METHOD"],
    ["EXTERNAL", "EXTERNAL"],
  ];

  const edgeTypes = [
    ["CONTAINS", "CONTAINS"],
    ["IMPORTS", "IMPORTS"],
    ["CALLS", "CALLS"],
    ["INHERITS", "INHERITS"],
  ];

  return (
    <div
      style={{
        padding: "15px",
        borderBottom: "1px solid #ddd",
        background: "#ffffff",
      }}
    >
      <h3>Node Filters</h3>

      <div
        style={{
          display: "flex",
          gap: "15px",
          flexWrap: "wrap",
        }}
      >
        {nodeTypes.map(([type, label]) => (
          <label key={type}>
            <input
              type="checkbox"
              checked={nodeFilters[type]}
              onChange={() => onNodeFilterChange(type)}
            />

            {" "}

            {label}
          </label>
        ))}
      </div>

      <h3>Relationship Filters</h3>

      <div
        style={{
          display: "flex",
          gap: "15px",
          flexWrap: "wrap",
        }}
      >
        {edgeTypes.map(([type, label]) => (
          <label key={type}>
            <input
              type="checkbox"
              checked={edgeFilters[type]}
              onChange={() => onEdgeFilterChange(type)}
            />

            {" "}

            {label}
          </label>
        ))}
      </div>
    </div>
  );
}

export default GraphControls;