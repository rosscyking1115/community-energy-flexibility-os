// Half-hour slot helpers + a small client-side scorer. The 48-slot curves come
// from the server (/v1/forecast); the /plan tool gets its windows and savings
// from the real /v1/optimise. This module is only for (a) parsing the API's
// "HH:MM-HH:MM" window strings into slots to draw on the band, and (b) the home
// hero's honest "tonight's cleanest window" demo, computed from the real curve.

export const SLOTS = 48;

/** Slot index (0–47, or 48 = 24:00) → "HH:MM". */
export function slotToClock(i: number): string {
  if (i >= SLOTS) return "24:00";
  const idx = ((i % SLOTS) + SLOTS) % SLOTS;
  const hh = Math.floor(idx / 2);
  return `${String(hh).padStart(2, "0")}:${idx % 2 ? "30" : "00"}`;
}

/** "HH:MM" → slot index. "24:00" → 48. */
export function clockToSlot(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  if (h === 24) return SLOTS;
  return h * 2 + (m >= 30 ? 1 : 0);
}

export interface Window {
  s: number; // start slot
  e: number; // end slot (exclusive; may equal 48)
  label?: string;
}

/** Parse an API window string like "03:30-05:00" into start/end slots. */
export function parseWindow(win: string): Window {
  const [a, b] = win.split("-");
  const s = clockToSlot(a.trim());
  let e = clockToSlot(b.trim());
  if (e <= s) e += SLOTS; // defensive; the engine rejects true wraps
  return { s, e };
}

/** Mean of a curve over [s, s+dur) with wrap. */
export function avg(arr: number[], s: number, dur: number): number {
  let t = 0;
  for (let k = 0; k < dur; k++) t += arr[(s + k) % SLOTS];
  return t / dur;
}

/**
 * Lowest-carbon run window for a duration inside [earliest, finishBy) — the
 * honest "cleanest slot tonight" the home hero brackets, straight from the real
 * carbon curve. Ties broken by lower price when a price curve is present.
 */
export function greenestWindow(
  carbon: number[],
  dur: number,
  earliest = 0,
  finishBy = SLOTS,
  price: number[] | null = null,
): Window {
  let best: { s: number; ac: number; ap: number } | null = null;
  for (let s = earliest; s + dur <= finishBy; s++) {
    const ac = avg(carbon, s, dur);
    const ap = price ? avg(price, s, dur) : 0;
    if (!best || ac < best.ac || (ac === best.ac && ap < best.ap)) best = { s, ac, ap };
  }
  const s = best?.s ?? earliest;
  return { s, e: s + dur };
}
