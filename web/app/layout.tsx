import type { Metadata } from "next";

import Masthead from "@/components/Masthead";

import "./globals.css";
import { plexMono, plexSans } from "./fonts";

export const metadata: Metadata = {
  title: "After Midnight — when to run flexible loads",
  description:
    "Find the cleanest, cheapest window to run flexible electricity loads, from live UK grid carbon and Octopus Agile prices. Planning advice only.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-GB" className={`${plexSans.variable} ${plexMono.variable}`}>
      <body>
        <a href="#cef-main" className="skip-link">
          Skip to content
        </a>
        <Masthead />
        <div id="cef-main" tabIndex={-1}>
          {children}
        </div>
      </body>
    </html>
  );
}
