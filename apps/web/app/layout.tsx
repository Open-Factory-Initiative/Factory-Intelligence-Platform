import type { Metadata } from "next";
import Link from "next/link";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Operations Workbench",
  description: "Simulator-backed Factory Intelligence Platform workbench shell.",
};

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/detections", label: "Detections" },
  { href: "/recommendations", label: "Recommendations" },
  { href: "/rca-capa-draft", label: "RCA/CAPA Draft" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="site-header">
            <div className="header-inner">
              <Link className="brand" href="/">
                <span className="brand-name">Factory Intelligence Platform</span>
                <span className="brand-context">Operations Workbench</span>
              </Link>
              <nav aria-label="Primary navigation" className="primary-nav">
                {navItems.map((item) => (
                  <Link className="nav-link" href={item.href} key={item.href}>
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
          </header>
          <main className="page-shell">{children}</main>
        </div>
      </body>
    </html>
  );
}
