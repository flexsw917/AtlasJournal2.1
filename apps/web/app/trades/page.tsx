"use client";

import { ColumnDef, createColumnHelper, flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";

import { Button, Card, Input } from "@/components/ui";
import { API_BASE_URL, apiFetch } from "@/lib/api";

interface Execution {
  id: number;
  side: string;
  qty: number;
  price: number;
  timestamp: string;
}

interface Trade {
  id: number;
  instrument: { symbol: string };
  direction: string;
  status: string;
  strategy?: string;
  net_pl: number;
  opened_at: string;
  closed_at?: string;
  executions: Execution[];
}

interface TradeResponse {
  items: Trade[];
  total: number;
}

export default function TradesPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({ symbol: "", strategy: "" });

  const columnHelper = createColumnHelper<Trade>();
  const columns = useMemo<ColumnDef<Trade, unknown>[]>(
    () => [
      columnHelper.accessor((row) => row.instrument.symbol, {
        header: "Symbol"
      }),
      columnHelper.accessor("direction", { header: "Direction" }),
      columnHelper.accessor("status", { header: "Status" }),
      columnHelper.accessor("strategy", { header: "Strategy" }),
      columnHelper.accessor("net_pl", {
        header: "Net P/L",
        cell: (info) => `$${info.getValue<number>().toFixed(2)}`
      }),
      columnHelper.accessor("opened_at", {
        header: "Opened",
        cell: (info) => new Date(info.getValue<string>()).toLocaleString()
      }),
      columnHelper.display({
        id: "actions",
        header: "",
        cell: (info) => (
          <a className="text-sm text-emerald-400" href={`/trades/${info.row.original.id}`}>
            View
          </a>
        )
      })
    ],
    [columnHelper]
  );

  const table = useReactTable({ data: trades, columns, getCoreRowModel: getCoreRowModel() });

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const query = new URLSearchParams();
        if (filters.symbol) query.set("symbol", filters.symbol);
        if (filters.strategy) query.set("strategy", filters.strategy);
        const data = await apiFetch<TradeResponse>(`/trades/?${query.toString()}`);
        setTrades(data.items);
        setTotal(data.total);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [filters]);

  const handleFilterChange = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    setFilters({
      symbol: String(formData.get("symbol") ?? ""),
      strategy: String(formData.get("strategy") ?? "")
    });
  };

  const handleExport = async () => {
    const query = new URLSearchParams();
    if (filters.symbol) query.set("symbol", filters.symbol);
    if (filters.strategy) query.set("strategy", filters.strategy);
    const data = await apiFetch<TradeResponse>(`/trades/?${query.toString()}&page_size=1000`);
    const header = ["symbol", "direction", "status", "strategy", "net_pl", "opened_at", "closed_at"];
    const rows = data.items.map((trade) => [
      trade.instrument.symbol,
      trade.direction,
      trade.status,
      trade.strategy ?? "",
      trade.net_pl.toFixed(2),
      trade.opened_at,
      trade.closed_at ?? ""
    ]);
    const csv = [header, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "trades.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Trades</h2>
        <Button onClick={handleExport}>Export CSV</Button>
      </div>
      <Card>
        <form className="grid gap-4 sm:grid-cols-3" onSubmit={handleFilterChange}>
          <label className="text-sm">
            Symbol
            <Input name="symbol" placeholder="AAPL" defaultValue={filters.symbol} />
          </label>
          <label className="text-sm">
            Strategy
            <Input name="strategy" placeholder="Breakout" defaultValue={filters.strategy} />
          </label>
          <div className="flex items-end">
            <Button type="submit" className="w-full">
              Apply filters
            </Button>
          </div>
        </form>
      </Card>
      <Card>
        {loading ? <p className="text-sm text-slate-400">Loading trades...</p> : null}
        {error ? <p className="text-sm text-rose-400">{error}</p> : null}
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="bg-slate-900/80">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id} className="px-4 py-2 text-left font-medium text-slate-400">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="border-t border-slate-800">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-2 text-slate-100">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-4 text-xs text-slate-500">Showing {trades.length} of {total} trades.</p>
      </Card>
    </div>
  );
}
