// Self-hosted type via next/font — no layout shift, no external request at
// runtime. IBM Plex Sans carries the display + body; IBM Plex Mono sets every
// figure (see DESIGN_NOTES.md). Exposed as CSS variables consumed in globals.css.
import { IBM_Plex_Mono, IBM_Plex_Sans } from "next/font/google";

export const plexSans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

export const plexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-mono",
  display: "swap",
});
