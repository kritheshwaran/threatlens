const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchScannerData(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, options);
  return response.json();
}
