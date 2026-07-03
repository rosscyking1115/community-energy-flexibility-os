// Client-side API helpers. They call the same-origin BFF routes (/api/*), never
// the API origin directly. Design components import these; they never see fetch.

import type {
  Appliance,
  OptimiseRequest,
  OptimiseResponse,
  Region,
} from "@/lib/types";

async function asJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const detail = await res
      .json()
      .then((b) => b?.detail)
      .catch(() => null);
    throw new Error(detail ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

export function getRegions(): Promise<Region[]> {
  return fetch("/api/regions").then((r) => asJson<Region[]>(r));
}

export function getAppliances(): Promise<Appliance[]> {
  return fetch("/api/appliances").then((r) => asJson<Appliance[]>(r));
}

export function optimise(body: OptimiseRequest): Promise<OptimiseResponse> {
  return fetch("/api/optimise", {
    method: "POST",
    body: JSON.stringify(body),
  }).then((r) => asJson<OptimiseResponse>(r));
}
