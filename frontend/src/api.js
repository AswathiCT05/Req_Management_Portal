const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Sends JSON requests to the backend and normalizes API errors.
async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(data?.detail || "Request failed");
  }

  return data;
}

// Calls the backend signup endpoint.
export function signup(payload) {
  return request("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

// Calls the backend login endpoint.
export function login(payload) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

// Loads a paginated page of requirements.
export function getRequirements(page = 1, limit = 10) {
  return request(`/requirements?page=${page}&limit=${limit}`);
}

// Creates a new requirement in the backend.
export function createRequirement(payload) {
  return request("/requirements", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
