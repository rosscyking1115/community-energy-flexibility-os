// Shared figure formatting. Savings are pence-based from the API; show small
// values in p and larger in £, and grams vs kg — always as tabular mono figures.
export function money(p: number): string {
  return p >= 100 ? `£${(p / 100).toFixed(2)}` : `${Math.round(p)}p`;
}

export function grams(g: number): string {
  return g >= 1000 ? `${(g / 1000).toFixed(2)} kg` : `${Math.round(g)} g`;
}
