import { useEffect, useState } from "react";
import { getFile } from "../../services/api";

function CodeViewer({ repositoryId, filePath }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!repositoryId || !filePath) {
      setFile(null);
      return;
    }

    async function loadFile() {
      try {
        setLoading(true);
        setError("");

        const data = await getFile(repositoryId, filePath);

        setFile(data);
      } catch (err) {
        setError(err.message);
        setFile(null);
      } finally {
        setLoading(false);
      }
    }

    loadFile();
  }, [repositoryId, filePath]);

  if (!filePath) {
    return (
      <div className="code-viewer-empty">
        Select a file or symbol to view its source code.
      </div>
    );
  }

  if (loading) {
    return <div className="code-viewer-empty">Loading code...</div>;
  }

  if (error) {
    return (
      <div className="code-viewer-empty code-error">
        {error}
      </div>
    );
  }

  if (!file) {
    return null;
  }

  return (
    <div className="code-viewer">
      <div className="code-header">
        <strong>{file.file}</strong>

        <span>
          {file.language} · {file.total_lines} lines
        </span>
      </div>

      <pre>
        <code>{file.content}</code>
      </pre>
    </div>
  );
}

export default CodeViewer;