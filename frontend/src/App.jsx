import ArchitectureGraph from "./components/Graph/ArchitectureGraph";

const REPOSITORY_ID = "fa6c9b49-a2f3-41ab-b62f-bdf6315e8755";

function App() {
  return (
    <div className="app">
      <h1>CodeAtlas Architecture Graph</h1>

      <ArchitectureGraph
        repositoryId={REPOSITORY_ID}
        nodeFilters={{
          FILE: true,
          CLASS: true,
          FUNCTION: true,
          METHOD: true,
          EXTERNAL: true,
        }}
        edgeFilters={{
          CONTAINS: true,
          IMPORTS: true,
          CALLS: true,
          INHERITS: true,
        }}
      />
    </div>
  );
}

export default App;
