"use client";

// PLACEHOLDER tool page. The wiring (data fetch via BFF, region/appliance/
// objective state, optimise call, result shape) is real and complete; the
// visual UI is intentionally bare for the design team to rebuild against these
// same hooks and the contract in lib/types.ts. See web/UI_SPEC.md.

import { useEffect, useState } from "react";

import { getAppliances, getRegions, optimise } from "@/lib/api";
import type {
  Appliance,
  Objective,
  OptimiseResponse,
  Region,
  TariffSpec,
  TaskSpec,
} from "@/lib/types";

export default function PlanPage() {
  const [regions, setRegions] = useState<Region[]>([]);
  const [appliances, setAppliances] = useState<Appliance[]>([]);
  const [regionId, setRegionId] = useState("");
  const [objective, setObjective] = useState<Objective>("balanced");
  const [tasks, setTasks] = useState<TaskSpec[]>([]);
  const [result, setResult] = useState<OptimiseResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getRegions()
      .then((r) => {
        setRegions(r);
        setRegionId(r[0]?.id ?? "");
      })
      .catch((e: Error) => setError(e.message));
    getAppliances().then(setAppliances).catch(() => undefined);
  }, []);

  const region = regions.find((r) => r.id === regionId);

  function addAppliance(id: string) {
    const a = appliances.find((x) => x.id === id);
    if (!a) return;
    setTasks((t) => [
      ...t,
      {
        name: a.name,
        device_type: a.name,
        energy_kwh: a.energy_kwh,
        duration_hours: a.duration_hours,
        earliest: a.typical_earliest,
        latest: a.typical_latest,
        preferred: null,
      },
    ]);
  }

  async function run() {
    setError(null);
    setBusy(true);
    setResult(null);
    try {
      const tariff: TariffSpec = region?.supports_agile
        ? { kind: "agile" }
        : { kind: "economy7", day_rate_p: 32, night_rate_p: 14, standing_charge_p: 45 };
      setResult(await optimise({ region_id: regionId, tariff, tasks, objective, cost_weight: 0.5 }));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
      <h1>Plan tomorrow</h1>
      {error && <p role="alert">⚠ {error}</p>}

      <label>
        Region:{" "}
        <select value={regionId} onChange={(e) => setRegionId(e.target.value)}>
          {regions.map((r) => (
            <option key={r.id} value={r.id}>
              {r.name}
            </option>
          ))}
        </select>
      </label>{" "}
      {region && !region.has_live_forecast && <em>(typical-day carbon profile)</em>}

      <p>
        Optimise for:{" "}
        <select value={objective} onChange={(e) => setObjective(e.target.value as Objective)}>
          <option value="cheapest">Cheapest</option>
          <option value="lowest_carbon">Lowest carbon</option>
          <option value="balanced">Balanced</option>
          <option value="avoid_peak">Avoid peak</option>
        </select>
      </p>

      <p>
        Add appliance:{" "}
        <select onChange={(e) => e.target.value && addAppliance(e.target.value)} value="">
          <option value="">Choose…</option>
          {appliances.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
      </p>

      <ul>
        {tasks.map((t, i) => (
          <li key={i}>
            {t.name} — {t.energy_kwh} kWh, {t.duration_hours} h
            {t.latest ? `, by ${t.latest}` : ""}
          </li>
        ))}
      </ul>

      <button onClick={run} disabled={busy || !regionId || tasks.length === 0}>
        {busy ? "Working…" : "Find the best times"}
      </button>

      {result && (
        <section>
          <h2>Your plan</h2>
          <p>
            Estimated saving: £{(result.total_cost_saving_p / 100).toFixed(2)} and{" "}
            {(result.total_carbon_saving_g / 1000).toFixed(2)} kg CO₂ · carbon:{" "}
            {result.carbon_source}
          </p>
          <ul>
            {result.tasks.map((t, i) => (
              <li key={i}>
                <strong>{t.device_type}</strong>: run {t.run_window} (instead of{" "}
                {t.baseline_window}) — saves {t.cost_saving_p.toFixed(0)}p /{" "}
                {t.carbon_saving_g.toFixed(0)} g · {t.confidence_band}
                <br />
                <small>{t.caveat}</small>
              </li>
            ))}
          </ul>
          <p>
            <small>{result.safety_statement}</small>
          </p>
        </section>
      )}
    </main>
  );
}
