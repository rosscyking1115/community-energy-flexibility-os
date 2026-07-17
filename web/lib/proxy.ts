import { API_BASE_URL } from "@/lib/config";

/**
 * The single point that talks to the API (the "BFF"). Client components hit
 * same-origin /api/* routes that call this — so the API origin stays hidden,
 * CORS is sidestepped entirely, and errors are shaped in one place (forward the
 * upstream status + detail; a network failure becomes a clean 503, never a
 * blanket 500).
 */
export async function proxy(path: string, init?: RequestInit): Promise<Response> {
  try {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
      cache: "no-store",
    });
    const body = await res.text();
    return new Response(body || "{}", {
      status: res.status,
      headers: { "content-type": "application/json" },
    });
  } catch {
    return Response.json(
      { detail: "The data service is unavailable. Please try again shortly." },
      { status: 503 },
    );
  }
}
