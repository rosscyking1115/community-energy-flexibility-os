import { slotToClock, type Window } from "@/lib/scoring";

// THE NIGHT BAND — the product's signature. One horizontal day, midnight→midnight.
// Grid carbon is drawn as ink bars whose height AND ink density (opacity) encode
// intensity — never colour. Price is a thin ink line (the second channel). The
// recommended run-window is an amber bracket + label. Baseline ("usual") starts
// are dashed ink ticks. Hand-rolled SVG, no chart library. Pure/presentational —
// safe in Server Components. Colours are literal hex (SVG presentation attributes
// don't read CSS custom properties) and mirror the tokens in globals.css.

const W = 1280;
const H = 240;
const PAD_X = 14;
const TOP = 78;
const BOTTOM = 202;
const PLOT_W = W - PAD_X * 2;
const PLOT_H = BOTTOM - TOP;
const SLOT_W = PLOT_W / 48;
const xAt = (i: number) => PAD_X + i * SLOT_W;

export interface DayBandProps {
  carbon: number[]; // 48 half-hourly gCO2/kWh
  price?: number[] | null; // 48 half-hourly p/kWh, or null (no price channel)
  windows?: Window[]; // recommended run-windows (amber brackets)
  baselines?: number[]; // baseline start slots ("usual" ticks)
  regionName: string;
  hasTable?: boolean; // mention the data-table equivalent in the aria-label
}

export default function DayBand({
  carbon,
  price = null,
  windows = [],
  baselines = [],
  regionName,
  hasTable = false,
}: DayBandProps) {
  const cmin = Math.min(...carbon);
  const cmax = Math.max(...carbon);
  const cRange = cmax - cmin || 1;
  let pmin = 0;
  let pRange = 1;
  if (price && price.length) {
    pmin = Math.min(...price);
    pRange = Math.max(...price) - pmin || 1;
  }
  const yP = (v: number) => BOTTOM - ((v - pmin) / pRange) * PLOT_H;

  const winTxt = windows
    .map((w) => `${slotToClock(w.s)} to ${slotToClock(w.e)}`)
    .join(", ");
  const label =
    `Twenty-four hour band from midnight to midnight for ${regionName}. ` +
    "Grid carbon intensity is drawn as bars — taller and darker means heavier — " +
    (price ? "and price as a line. " : "carbon only. ") +
    (winTxt ? `Recommended run windows: ${winTxt}. ` : "") +
    (hasTable ? "A data table with the same half-hourly figures is available." : "");

  const pricePath = price
    ? price
        .map(
          (v, i) =>
            `${i ? "L" : "M"}${(xAt(i) + SLOT_W / 2).toFixed(1)} ${yP(v).toFixed(1)}`,
        )
        .join(" ")
    : "";

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      width="100%"
      style={{ display: "block", minWidth: "640px" }}
      role="img"
      aria-label={label}
    >
      {/* baseline rule + faint 6-hour gridlines */}
      <line x1={PAD_X} y1={BOTTOM} x2={W - PAD_X} y2={BOTTOM} stroke="#c0c9d2" strokeWidth={1} />
      {[0, 12, 24, 36, 48].map((i) => (
        <line key={`g${i}`} x1={xAt(i)} y1={TOP - 6} x2={xAt(i)} y2={BOTTOM} stroke="#ced6de" strokeWidth={1} />
      ))}

      {/* recommended window washes (amber = "run here") */}
      {windows.map((w, wi) => (
        <rect
          key={`wash${wi}`}
          x={xAt(w.s)}
          y={TOP - 2}
          width={Math.max(2, xAt(w.e) - xAt(w.s))}
          height={BOTTOM - TOP + 2}
          fill="rgba(228,161,27,0.16)"
        />
      ))}

      {/* carbon bars — intensity by height AND ink density (opacity), never colour */}
      {carbon.map((v, i) => {
        const t = (v - cmin) / cRange;
        const bh = 6 + t * (PLOT_H - 6);
        const bw = SLOT_W * 0.6;
        return (
          <rect
            key={`bar${i}`}
            x={xAt(i) + (SLOT_W - bw) / 2}
            y={BOTTOM - bh}
            width={bw}
            height={bh}
            fill="#2e3a46"
            opacity={0.42 + 0.53 * t}
            rx={0.5}
          />
        );
      })}

      {/* price line — the second channel */}
      {pricePath && (
        <path d={pricePath} fill="none" stroke="#1a1d21" strokeWidth={1.6} strokeLinejoin="round" opacity={0.9} />
      )}

      {/* baseline "usual" markers */}
      {baselines.map((b, bi) => {
        const bx = xAt(b) + SLOT_W / 2;
        return (
          <g key={`bl${bi}`}>
            <line x1={bx} y1={TOP - 2} x2={bx} y2={BOTTOM} stroke="#1a1d21" strokeWidth={1.25} strokeDasharray="2 3" opacity={0.7} />
            <text x={bx} y={BOTTOM + 30} textAnchor="middle" fontSize={11} fontFamily="var(--font-mono)" fill="#5b636c">
              usual
            </text>
          </g>
        );
      })}

      {/* amber brackets + labels (the identity) — stacked in tiers so they never collide */}
      {windows.map((w, wi) => {
        const xs = xAt(w.s);
        const xe = xAt(w.e);
        const by = TOP - 18 - wi * 20;
        const text = w.label ?? `run ${slotToClock(w.s)}–${slotToClock(w.e)}`;
        return (
          <g key={`brk${wi}`}>
            <path
              d={`M${xs.toFixed(1)} ${by + 9} L${xs.toFixed(1)} ${by} L${xe.toFixed(1)} ${by} L${xe.toFixed(1)} ${by + 9}`}
              fill="none"
              stroke="#e4a11b"
              strokeWidth={2.4}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <text
              x={Math.max(xs + 2, (xs + xe) / 2)}
              y={by - 5}
              textAnchor="middle"
              fontSize={12.5}
              fontWeight={600}
              fontFamily="var(--font-mono)"
              fill="#1a1d21"
            >
              {text}
            </text>
          </g>
        );
      })}

      {/* x-axis labels */}
      {["00:00", "06:00", "12:00", "18:00", "24:00"].map((t, k) => (
        <text
          key={`xt${k}`}
          x={xAt(k * 12)}
          y={H - 6}
          textAnchor={k === 0 ? "start" : k === 4 ? "end" : "middle"}
          fontSize={11.5}
          fontFamily="var(--font-mono)"
          fill="#5b636c"
        >
          {t}
        </text>
      ))}
    </svg>
  );
}
