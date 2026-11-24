import axios from "axios";

// Backend URL: set VITE_API_URL when deploying (e.g. on Vercel).
export const API_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

// Each browser gets its own private workspace on the backend, so visitors
// of the public demo never see each other's transcripts.
function getWorkspaceId() {
  const KEY = "ric-workspace";
  let id = localStorage.getItem(KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(KEY, id);
  }
  return id;
}

export const WORKSPACE_HEADERS = { "X-Workspace": getWorkspaceId() };

export const api = axios.create({
  baseURL: API_URL,
  headers: WORKSPACE_HEADERS,
});
