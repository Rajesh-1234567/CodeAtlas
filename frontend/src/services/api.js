const API_BASE_URL = "http://localhost:8000";

async function handleResponse(response) {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const data = await response.json();

      if (data.detail) {
        message = data.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(message);
  }

  return response.json();
}

export async function getRepositoryGraph(repositoryId) {
  const response = await fetch(
    `${API_BASE_URL}/repositories/${repositoryId}/graph`
  );

  return handleResponse(response);
}

export async function searchRepository(repositoryId, query) {
  const response = await fetch(
    `${API_BASE_URL}/repositories/${repositoryId}/search`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
      }),
    }
  );

  return handleResponse(response);
}

export async function getFile(repositoryId, filePath) {
  const encodedPath = filePath
    .split("/")
    .map(encodeURIComponent)
    .join("/");

  const response = await fetch(
    `${API_BASE_URL}/repositories/${repositoryId}/files/${encodedPath}`
  );

  return handleResponse(response);
}