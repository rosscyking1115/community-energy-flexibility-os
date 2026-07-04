// Root loading state (App Router). A shimmer skeleton of the band + rows so a
// route with server work never feels frozen. Reduced-motion disables the shimmer
// (globals.css). Mirrors the /plan loading skeleton for continuity.
const shimmer: React.CSSProperties = {
  background:
    "linear-gradient(90deg,#dde3e9 0%,#eff3f6 45%,#dde3e9 90%)",
  backgroundSize: "520px 100%",
  animation: "cef-shimmer 1.4s linear infinite",
};

export default function Loading() {
  return (
    <main style={{ maxWidth: "var(--col)", margin: "0 auto", padding: "42px var(--pad-x)" }}>
      <p
        className="mono"
        style={{
          fontSize: 12,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          color: "var(--slate)",
          margin: "0 0 16px",
        }}
      >
        Reading the forecast…
      </p>
      <div style={{ ...shimmer, width: "100%", height: 180, border: "1px solid var(--line)", borderRadius: "var(--radius-lg)", marginBottom: 14 }} />
      <div style={{ ...shimmer, height: 60, borderRadius: 8, marginBottom: 12 }} />
      <div style={{ ...shimmer, height: 60, borderRadius: 8 }} />
    </main>
  );
}
