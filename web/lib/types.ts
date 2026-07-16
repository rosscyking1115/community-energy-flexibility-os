// Pydantic/OpenAPI is the source of truth. `npm run gen:types` regenerates the
// checked-in schema bindings in types.gen.ts; this module gives the app concise
// names and preserves optionality for request fields that the API defaults.

import type { components } from "./types.gen";

type Schemas = components["schemas"];

export type Region = Schemas["RegionOut"];
export type Appliance = Schemas["ApplianceOut"];
export type Forecast = Schemas["ForecastOut"];
export type ScheduledTask = Schemas["ScheduledTaskOut"];
export type OptimiseResponse = Schemas["OptimiseResponse"];

type GeneratedTariffSpec = Schemas["TariffSpec"];
export type TariffKind = GeneratedTariffSpec["kind"];
export type TariffSpec = Omit<GeneratedTariffSpec, "standing_charge_p"> & {
  standing_charge_p?: number;
};

type GeneratedTaskSpec = Schemas["TaskSpec"];
export type TaskSpec = Omit<GeneratedTaskSpec, "earliest" | "latest"> & {
  earliest?: string;
  latest?: string;
};

type GeneratedOptimiseRequest = Schemas["OptimiseRequest"];
export type Objective = GeneratedOptimiseRequest["objective"];
export type OptimiseRequest = Omit<
  GeneratedOptimiseRequest,
  "tariff" | "tasks" | "cost_weight"
> & {
  tariff: TariffSpec;
  tasks: TaskSpec[];
  cost_weight?: number;
};
