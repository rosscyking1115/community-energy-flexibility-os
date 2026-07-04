"use client";

// Route error boundary, in product voice — never a raw stack. Errors don't
// apologise and are never vague: say what happened and how to recover.
export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main style={{ maxWidth: 660, margin: "0 auto", padding: "54px var(--pad-x)" }}>
      <div
        role="alert"
        style={{
          border: "1px solid var(--line)",
          borderLeft: "4px solid var(--filament)",
          borderRadius: 8,
          background: "var(--panel)",
          padding: 26,
        }}
      >
        <p
          className="mono"
          style={{ fontSize: 12, letterSpacing: "0.12em", textTransform: "uppercase", color: "var(--slate)", margin: "0 0 10px" }}
        >
          Something went wrong
        </p>
        <h1 style={{ fontWeight: 700, fontSize: 22, margin: "0 0 10px", letterSpacing: "-0.01em" }}>
          This page didn&apos;t load.
        </h1>
        <p style={{ margin: "0 0 20px", fontSize: 15.5, color: "var(--ink-soft-2)", lineHeight: 1.55 }}>
          A hitch on our side, not yours. Try again — if it keeps happening the
          forecast service may be briefly down.
        </p>
        <button type="button" onClick={reset} style={ctaPrimary}>
          Try again
        </button>
      </div>
    </main>
  );
}

const ctaPrimary: React.CSSProperties = {
  fontSize: 16,
  fontWeight: 600,
  color: "var(--paper)",
  background: "var(--ink)",
  border: "1px solid var(--ink)",
  borderRadius: 7,
  padding: "13px 22px",
  cursor: "pointer",
  minHeight: 24,
};
