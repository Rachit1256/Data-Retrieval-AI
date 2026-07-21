import axios from "axios";

// In production (Vercel), set VITE_API_BASE in the project's
// Environment Variables to your deployed backend's URL, e.g.
// https://your-backend.onrender.com (no trailing slash).
// Locally, it falls back to the FastAPI dev server default, so nothing
// changes for local development.
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

const api = axios.create({
    baseURL: API_BASE,
});

// Chart tool responses from the backend return a bare filename
// (e.g. "3f9a....png") that lives under the /charts static mount.
// Build the actual browser-loadable URL from it in one place.
export function chartUrl(filename) {
    if (!filename) return null;
    return `${API_BASE}/charts/${filename}`;
}

export default api;
