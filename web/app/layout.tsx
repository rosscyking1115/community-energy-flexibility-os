import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Community Energy Flexibility OS",
  description:
    "Find the best times to run flexible electricity loads to cut cost and carbon. Planning advice only.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-GB">
      <body>{children}</body>
    </html>
  );
}
