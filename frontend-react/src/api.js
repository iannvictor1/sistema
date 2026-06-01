const API_BASE = import.meta.env.VITE_API_BASE ?? (import.meta.env.DEV ? "/api" : "");

async function request(path, options = {}) {
  const loggedUser = localStorage.getItem("bonificacao_user");
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(loggedUser ? { "X-Bonificacao-User": loggedUser } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Erro HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  return response;
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body) }),
  put: (path, body) => request(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: "DELETE" }),
};

export const downloadUrl = (path) => `${API_BASE}${path}`;
