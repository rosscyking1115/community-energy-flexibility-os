// Contract types mirroring api/community_energy_api/models.py — that pydantic
// module is the SOURCE OF TRUTH. Regenerate strict types from the live OpenAPI
// with `npm run gen:types` (needs the API running) and import from
// lib/types.gen.ts when you want generated types instead of these hand-mirrored
// ones. Keep this file in sync with models.py until then.

export interface Region {
  id: string;
  name: string;
  nation: string;
  carbon_source: string;
  has_live_forecast: boolean;
  supports_agile: boolean;
}

export interface Appliance {
  id: string;
  name: string;
  category: string;
  energy_kwh: number;
  duration_hours: number;
  typical_earliest: string;
  typical_latest: string;
  noise_sensitive: boolean;
}

export type TariffKind = "flat" | "economy7" | "agile" | "manual_half_hourly";

export interface TariffSpec {
  kind: TariffKind;
  standing_charge_p?: number;
  unit_rate_p?: number;
  day_rate_p?: number;
  night_rate_p?: number;
  prices_p?: number[];
}

export type Objective = "cheapest" | "lowest_carbon" | "balanced" | "avoid_peak";

export interface TaskSpec {
  name: string;
  device_type: string;
  energy_kwh: number;
  duration_hours: number;
  earliest?: string;
  latest?: string;
  preferred?: string | null;
}

export interface OptimiseRequest {
  region_id: string;
  tariff: TariffSpec;
  tasks: TaskSpec[];
  objective: Objective;
  cost_weight?: number;
}

export interface ScheduledTask {
  name: string;
  device_type: string;
  run_window: string;
  baseline_window: string;
  cost_saving_p: number;
  carbon_saving_g: number;
  confidence: number;
  confidence_band: string;
  caveat: string;
}

export interface OptimiseResponse {
  objective: string;
  region: string;
  carbon_source: string;
  total_cost_saving_p: number;
  total_carbon_saving_g: number;
  tasks: ScheduledTask[];
  safety_statement: string;
}
