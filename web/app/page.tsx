import Link from "next/link";

import BandLegend from "@/components/BandLegend";
import DayBand from "@/components/DayBand";
import { money, grams } from "@/lib/format";
import { avg, greenestWindow, slotToClock } from "@/lib/scoring";
import { getForecastServer } from "@/lib/server-data";

// Home is a Server Component: it fetches tonight's real forecast for a default
// region once and brackets the genuinely cleanest overnight window — a live
// recommendation, not a marketing hero. Degrades gracefully if the feed is down.
const HERO_REGION = "south-west-england";
const HERO_REGION_NAME = "South West England";
const WASH_DUR = 3; // slots (1.5h)
const WASH_KWH = 0.8;
const BASELINE_SLOT = 38; // 19:00 — a typical evening start

export const dynamic = "force-dynamic"; // always fetch current runtime provenance

export default async function Home() {
  const forecast = await getForecastServer(HERO_REGION);
  const isLive = forecast?.is_live_forecast === true;

  let band = null;
  let cleanest = "";
  let saved = "";
  if (forecast) {
    const win = greenestWindow(forecast.carbon_g, WASH_DUR, 0, 16, forecast.price_p);
    win.label = `run ${slotToClock(win.s)}–${slotToClock(win.e)}`;
    cleanest = `${slotToClock(win.s)}–${slotToClock(win.e)}`;
    const saveG = Math.max(
      0,
      Math.round(WASH_KWH * (avg(forecast.carbon_g, BASELINE_SLOT, WASH_DUR) - avg(forecast.carbon_g, win.s, WASH_DUR))),
    );
    const saveP = forecast.price_p
      ? Math.max(0, Math.round(WASH_KWH * (avg(forecast.price_p, BASELINE_SLOT, WASH_DUR) - avg(forecast.price_p, win.s, WASH_DUR))))
      : 0;
    saved = forecast.price_p ? `${money(saveP)} · ${grams(saveG)}` : grams(saveG);
    band = (
      <DayBand
        carbon={forecast.carbon_g}
        price={forecast.price_p}
        windows={[win]}
        baselines={[BASELINE_SLOT]}
        regionName={forecast.region}
      />
    );
  }

  return (
    <main>
      <div style={{ maxWidth: "var(--col)", margin: "0 auto", padding: "56px var(--pad-x) 26px" }}>
        <p className="mono" style={{ ...eyebrow, display: "flex", alignItems: "center", gap: 10 }}>
          {isLive && <span aria-hidden="true" style={liveDot} />}
          {isLive ? `Live forecast · ${HERO_REGION_NAME}` : `${forecast?.carbon_source_label ?? "Data unavailable"} · illustrative timing`}
        </p>
        <h1 style={{ fontWeight: 700, fontSize: "clamp(32px,5.4vw,54px)", lineHeight: 1.04, letterSpacing: "-0.03em", margin: "0 0 18px", maxWidth: "17ch", textWrap: "balance" }}>
          Find a lower-cost, lower-carbon time to run flexible loads.
        </h1>
        <p style={{ fontSize: "clamp(16px,2.2vw,19px)", lineHeight: 1.55, maxWidth: "54ch", color: "var(--ink-soft-2)", margin: 0 }}>
          One horizontal day, midnight to midnight. The dark bars are how heavy
          the grid is each half-hour; the amber bracket is the cleanest, cheapest
          window to run a flexible load. That&apos;s the whole idea.
        </p>
      </div>

      {/* full-bleed signature band */}
      <section aria-labelledby="hero-band-h" style={{ width: "100%", background: "var(--paper-band)", borderTop: "1px solid var(--line)", borderBottom: "1px solid var(--line)", padding: "22px 0 14px" }}>
        <h2 id="hero-band-h" className="visually-hidden">
          Tonight&apos;s grid intensity for {HERO_REGION_NAME}
        </h2>
        <div style={{ maxWidth: "var(--col-band)", margin: "0 auto", padding: "0 var(--pad-x)" }}>
          {band ? (
            <>
              <BandLegend hasPrice={!!forecast?.price_p} hasBaseline />
              {band}
            </>
          ) : (
            <p className="mono" style={{ fontSize: 13, color: "var(--slate)", padding: "40px 0" }}>
              The planning curve is currently unavailable. Try the planner again shortly.
            </p>
          )}
        </div>
      </section>

      <div style={{ maxWidth: "var(--col)", margin: "0 auto", padding: "26px var(--pad-x) 84px" }}>
        {forecast && (
          <div style={{ border: "1px solid var(--line)", background: "var(--panel)", borderRadius: "var(--radius-lg)", padding: "20px 22px", display: "flex", flexWrap: "wrap", gap: "26px 40px", alignItems: "flex-end", margin: "0 0 44px" }}>
            <div>
              <p className="mono" style={figLabel}>{isLive ? "Cleanest window in this forecast" : "Lowest-carbon window in this illustrative profile"}</p>
              <p className="mono" style={bigFig}>{cleanest}</p>
            </div>
            <div style={{ height: 44, width: 1, background: "var(--line)", alignSelf: "center" }} />
            <div>
              <p className="mono" style={figLabel}>{isLive ? "Forecast saving for a typical wash" : "Illustrative saving for a typical wash"}</p>
              <p className="mono" style={bigFig}>{saved}</p>
            </div>
            <p className="mono" style={{ margin: 0, flex: "1 1 220px", minWidth: 200, fontSize: 12.5, color: "var(--slate)", lineHeight: 1.5 }}>
              vs a 19:00 start · {WASH_KWH} kWh load<br />
              {forecast.price_p ? "Octopus Agile" : "No live price curve"} · {forecast.carbon_source_label}
            </p>
          </div>
        )}

        {forecast?.is_fallback && (
          <p role="status" style={{ ...panelNote, margin: "-26px 0 36px" }}>
            This recommendation uses a labelled GB sample profile because the live carbon feed was unavailable. Treat the timing and saving as illustrative.
          </p>
        )}

        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", margin: "0 0 56px" }}>
          <Link href="/plan" style={ctaPrimary}>Plan your own loads →</Link>
          <Link href="/methodology" style={ctaGhost}>How we work it out</Link>
        </div>

        {/* honest ledger — tabular, not cards */}
        <div style={{ borderTop: "2px solid var(--ink)" }}>
          {LEDGER.map((row, i) => (
            <div key={i} style={{ display: "grid", gridTemplateColumns: "minmax(90px,150px) 1fr", gap: "18px 28px", padding: "18px 0", borderBottom: "1px solid var(--line)", alignItems: "baseline" }}>
              <p className="mono" style={{ margin: 0, fontWeight: 600, fontSize: 26, letterSpacing: "-0.01em" }}>{row.figure}</p>
              <p style={{ margin: 0, fontSize: 15, color: "var(--ink-soft-2)", lineHeight: 1.5, maxWidth: "52ch" }}>{row.text}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}

const LEDGER = [
  { figure: "2", text: "decision criteria: tariff cost and regional grid carbon, scored across each feasible start time." },
  { figure: "48", text: "half-hourly price and carbon points a day. Live inputs are labelled; sample and typical profiles remain visibly illustrative." },
  { figure: "0", text: "accounts, adverts, or automation. It advises; you decide when to press start." },
];

const eyebrow: React.CSSProperties = { fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase", color: "var(--slate)", margin: "0 0 20px" };
const liveDot: React.CSSProperties = { width: 7, height: 7, borderRadius: "50%", background: "var(--filament)", display: "inline-block", boxShadow: "0 0 0 3px var(--amber-chip)" };
const panelNote: React.CSSProperties = { border: "1px solid var(--line)", borderLeft: "4px solid var(--filament)", borderRadius: 7, padding: "13px 15px", color: "var(--ink-soft-2)", fontSize: 13.5, lineHeight: 1.5 };
const figLabel: React.CSSProperties = { fontSize: 11, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--slate)", margin: "0 0 7px" };
const bigFig: React.CSSProperties = { margin: 0, fontWeight: 600, fontSize: "clamp(26px,4vw,38px)", letterSpacing: "-0.01em", lineHeight: 1 };
const ctaPrimary: React.CSSProperties = { fontSize: 16, fontWeight: 600, color: "var(--paper)", background: "var(--ink)", border: "1px solid var(--ink)", borderRadius: 7, padding: "13px 22px", textDecoration: "none", minHeight: 24, display: "inline-flex", alignItems: "center" };
const ctaGhost: React.CSSProperties = { fontSize: 15, fontWeight: 500, color: "var(--ink)", background: "transparent", border: "1px solid var(--line-strong)", borderRadius: 7, padding: "11px 18px", textDecoration: "none", minHeight: 24, display: "inline-flex", alignItems: "center" };
