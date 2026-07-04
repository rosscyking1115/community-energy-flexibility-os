import "server-only";

import { API_BASE_URL } from "@/lib/config";
import type { Forecast } from "@/lib/types";

// Server-side fetch for Server Components (the home hero band). Talks to the API
// origin directly — same trust boundary as the BFF, never reaches the browser.
// Degrades to null on any failure so the page renders a graceful fallback
// rather than throwing (the playbook's "designed degradation per dependency").
export async function getForecastServer(regionId: string): Promise<Forecast | null> {
  try {
    const res = await fetch(
      `${API_BASE_URL}/v1/forecast/${encodeURIComponent(regionId)}`,
      { cache: "no-store" },
    );
    if (!res.ok) return null;
    return (await res.json()) as Forecast;
  } catch {
    return null;
  }
}
