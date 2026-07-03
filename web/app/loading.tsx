// Root loading state (App Router convention). Shown while a route with server
// work resolves, so navigation never feels frozen. Design will style this.
export default function Loading() {
  return <p style={{ padding: 24 }}>Loading…</p>;
}
