"use client";

import { useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { apiFetch } from "@/lib/api";
import { Card } from "@/components/ui";

type MetricsSummary = {
  realized_pl: number;
  win_rate: number;
  expectancy: number;
  profit_factor: number;
};

type EquityPoint = {
  date: string;
  equity: number;
};

export default function DashboardPage() {
  const [summary, setSummary] = useState<MetricsSummary | null>(null);
  const [points, setPoints] = useState<EquityPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [summaryResponse, equityResponse] = await Promise.all([
          apiFetch<MetricsSummary>("/metrics/summary"),
          apiFetch<{ points: EquityPoint[] }>("/metrics/equity_curve")
        ]);
        setSummary(summaryResponse);
        setPoints(equityResponse.points);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Dashboard</h2>
      {loading ? <p className="text-sm text-slate-400">Loading metrics...</p> : null}
      {error ? <p className="text-sm text-rose-400">{error}</p> : null}
      {summary ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card>
            <h3 className="text-sm text-slate-400">Realized P/L</h3>
            <p className="mt-2 text-2xl font-semibold">${summary.realized_pl.toFixed(2)}</p>
          </Card>
          <Card>
            <h3 className="text-sm text-slate-400">Win rate</h3>
            <p className="mt-2 text-2xl font-semibold">{(summary.win_rate * 100).toFixed(1)}%</p>
          </Card>
          <Card>
            <h3 className="text-sm text-slate-400">Expectancy</h3>
            <p className="mt-2 text-2xl font-semibold">${summary.expectancy.toFixed(2)}</p>
          </Card>
          <Card>
            <h3 className="text-sm text-slate-400">Profit factor</h3>
            <p className="mt-2 text-2xl font-semibold">{summary.profit_factor.toFixed(2)}</p>
          </Card>
        </div>
      ) : null}

      <Card>
        <h3 className="mb-4 text-sm text-slate-400">Equity curve</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer>
            <LineChart data={points}>
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Line type="monotone" dataKey="equity" stroke="#34d399" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
