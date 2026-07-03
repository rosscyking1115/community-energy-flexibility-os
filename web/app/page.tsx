import Link from "next/link";

// PLACEHOLDER home page — the design team builds the real landing page. This
// only proves routing works and links into the tool.
export default function Home() {
  return (
    <main style={{ maxWidth: 640, margin: "0 auto", padding: 24 }}>
      <h1>Community Energy Flexibility OS</h1>
      <p>
        Find the best times to run your flexible appliances to cut cost and
        carbon. Planning advice only — no guaranteed savings.
      </p>
      <p>
        <Link href="/plan">Plan tomorrow →</Link>
      </p>
    </main>
  );
}
