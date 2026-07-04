"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import styles from "./Masthead.module.css";

// Sticky masthead. The logo is a 5-bar mini "band" glyph — the signature in
// miniature — with the 4th bar amber. Active nav state derives from the route.
const NAV = [
  { href: "/", label: "Home" },
  { href: "/plan", label: "Plan" },
  { href: "/methodology", label: "Method" },
] as const;

const GLYPH = [
  { h: 7, amber: false },
  { h: 12, amber: false },
  { h: 18, amber: false },
  { h: 9, amber: true },
  { h: 5, amber: false },
];

export default function Masthead() {
  const pathname = usePathname();
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link href="/" className={styles.brand}>
          <span aria-hidden="true" className={styles.glyph}>
            {GLYPH.map((b, i) => (
              <span key={i} style={{ height: b.h, background: b.amber ? "var(--filament)" : undefined }} />
            ))}
          </span>
          <span className={styles.word}>After Midnight</span>
          <span className={`mono ${styles.tag}`}>Grid flexibility</span>
        </Link>
        <nav aria-label="Primary" className={styles.nav}>
          {NAV.map((n) => {
            const active = n.href === "/" ? pathname === "/" : pathname.startsWith(n.href);
            return (
              <Link
                key={n.href}
                href={n.href}
                className={active ? styles.on : styles.off}
                aria-current={active ? "page" : undefined}
              >
                {n.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
