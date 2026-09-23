function GraphControls({
  nodeFilters,
  setNodeFilters,
  edgeFilters,
  setEdgeFilters,
}) {
  const nodeTypes = ["FILE", "CLASS", "FUNCTION", "METHOD", "EXTERNAL"];

  const edgeTypes = ["CONTAINS", "IMPORTS", "CALLS", "INHERITS"];

  function toggleFilter(setter, value) {
    setter((current) => ({
      ...current,
      [value]: !current[value],
    }));
  }

  return (
    <div
      style={{
        padding: "12px",
        borderBottom: "1px solid #e5e7eb",
        background: "#ffffff",
      }}
    >
      <div style={{ marginBottom: "10px" }}>
        <strong>Node Filters</strong>

        <div
          style={{
            display: "flex",
            gap: "8px",
            flexWrap: "wrap",
            marginTop: "8px",
          }}
        >
          {nodeTypes.map((type) => (
            <label key={type} style={{ fontSize: "13px" }}>
              <input
                type="checkbox"
                checked={nodeFilters[type]}
                onChange={() => toggleFilter(setNodeFilters, type)}
              />{" "}
              {type}
            </label>
          ))}
        </div>
      </div>

      <div>
        <strong>Relationship Filters</strong>

        <div
          style={{
            display: "flex",
            gap: "8px",
            flexWrap: "wrap",
            marginTop: "8px",
          }}
        >
          {edgeTypes.map((type) => (
            <label key={type} style={{ fontSize: "13px" }}>
              <input
                type="checkbox"
                checked={edgeFilters[type]}
                onChange={() => toggleFilter(setEdgeFilters, type)}
              />{" "}
              {type}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

export default GraphControls;