// Core fetch wrapper: base URL, JSON handling, auth header injection,
// and a single place that reacts to an expired/invalid token.

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const TOKEN_KEY = 'threatlens_token';

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem(TOKEN_KEY);
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (networkErr) {
    throw new ApiError('Could not reach the ThreatLens API. Check your connection and try again.', 0);
  }

  if (response.status === 401) {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem('threatlens_user');
    window.dispatchEvent(new CustomEvent('threatlens:unauthorized'));
    throw new ApiError('Your session has expired. Please log in again.', 401);
  }

  let data = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const detail = data && (data.detail || data.message);
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg || JSON.stringify(d)).join('; ')
      : detail || `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return data;
}

export { API_BASE_URL, TOKEN_KEY };