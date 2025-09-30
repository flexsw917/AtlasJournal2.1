import "./globals.css";
import { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 min-h-screen">
        <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-8">
          <header className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold">ZellaLite</h1>
              <p className="text-sm text-slate-400">Trade journal built for fast iteration.</p>
            </div>
            <nav className="flex gap-4 text-sm text-slate-300">
              <a href="/dashboard" className="hover:text-white">
                Dashboard
              </a>
              <a href="/trades" className="hover:text-white">
                Trades
              </a>
              <a href="/import" className="hover:text-white">
                Import
              </a>
              <a href="/settings" className="hover:text-white">
                Settings
              </a>
            </nav>
          </header>
          <main className="flex-1">{children}</main>
        </div>
      </body>
    </html>
  );
}
