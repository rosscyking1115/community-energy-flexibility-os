// The band's channel legend, in HTML above the SVG so it's selectable and
// accessible (not baked into the chart). Swatches are tiny presentational
// primitives, so their dimensions live inline.
export default function BandLegend({
  hasPrice = true,
  hasBaseline = false,
}: {
  hasPrice?: boolean;
  hasBaseline?: boolean;
}) {
  return (
    <div
      className="mono"
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "8px 20px",
        margin: "0 0 6px",
        fontSize: "11.5px",
        color: "var(--slate)",
      }}
    >
      <span style={item}>
        <span aria-hidden="true" style={{ width: 9, height: 14, background: "var(--curve)", display: "inline-block" }} />
        bars · carbon gCO₂/kWh
      </span>
      {hasPrice && (
        <span style={item}>
          <span aria-hidden="true" style={{ width: 18, height: 0, borderTop: "2px solid var(--ink)", display: "inline-block" }} />
          line · price p/kWh
        </span>
      )}
      <span style={item}>
        <span aria-hidden="true" style={{ width: 16, height: 10, border: "2px solid var(--filament)", borderBottom: "none", display: "inline-block" }} />
        amber bracket · run here
      </span>
      {hasBaseline && (
        <span style={item}>
          <span aria-hidden="true" style={{ width: 0, height: 14, borderLeft: "2px dashed var(--ink)", display: "inline-block" }} />
          usual · your baseline
        </span>
      )}
    </div>
  );
}

const item: React.CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: "7px",
};
