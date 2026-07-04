import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Method — After Midnight",
  description: "How the recommended window and the saving are worked out.",
};

const ROWS = [
  {
    h: "The baseline is your habit",
    p: "Every saving is measured against the usual start you tell us — not a best case or a national average. If you would normally run the wash at 19:00, that is the number the recommended window is compared to. Change the baseline and the saving changes with it.",
  },
  {
    h: "Two channels: price and carbon",
    p: "Price comes from your tariff — half-hourly Octopus Agile rates, or the Economy 7 / flat rate you enter. Carbon comes from the regional forecast, drawn as the band's bars. We score each possible start on both and let you weight which matters more.",
  },
  {
    h: "Carbon is regional, not per-postcode",
    p: 'Grid carbon intensity is published by region (a GSP group), so we say "South West England region", never your street. Northern Ireland has no live GB feed, so we use a typical-day EirGrid profile and label it as such.',
  },
  {
    h: "Confidence, not certainty",
    p: "Forecasts move. A High-confidence window sits in a broad, stable trough where a small error will not change the advice. Low means the saving is real but sensitive to how the day turns out. This is decision support — you decide.",
  },
];

export default function Methodology() {
  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: "54px var(--pad-x) 88px" }}>
      <p className="mono" style={{ fontSize: 12, letterSpacing: "0.14em", textTransform: "uppercase", color: "var(--slate)", margin: "0 0 16px" }}>
        Method
      </p>
      <h1 style={{ fontWeight: 700, fontSize: "clamp(28px,4.4vw,42px)", lineHeight: 1.08, letterSpacing: "-0.025em", margin: "0 0 28px", maxWidth: "18ch" }}>
        How the window and the saving are worked out.
      </h1>
      <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
        {ROWS.map((m) => (
          <div key={m.h}>
            <h2 style={{ fontWeight: 600, fontSize: 20, margin: "0 0 8px", letterSpacing: "-0.01em" }}>{m.h}</h2>
            <p style={{ margin: 0, fontSize: 16, color: "var(--ink-soft)", lineHeight: 1.62 }}>{m.p}</p>
          </div>
        ))}
        <div style={{ borderTop: "1px solid var(--line)", paddingTop: 20 }}>
          <p style={{ margin: 0, fontSize: 13.5, color: "var(--slate)", lineHeight: 1.6 }}>
            Open source. Price: Octopus Agile API. Carbon: NESO / National Grid
            Carbon Intensity regional forecast (GB); EirGrid typical-day profile
            (Northern Ireland). Appliance energy figures are typical published
            values — adjust them to your own if you know them.
          </p>
        </div>
      </div>
    </main>
  );
}
