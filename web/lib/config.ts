// The API origin. Server-side only (used in BFF route handlers), so it never
// reaches the browser. Falls back to local dev if unset.
export const API_BASE_URL = process.env.API_BASE_URL ?? "http://127.0.0.1:8000";
