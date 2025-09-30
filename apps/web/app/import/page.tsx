"use client";

import { useState } from "react";

import { Button, Card, Input } from "@/components/ui";
import { API_BASE_URL, apiFetch } from "@/lib/api";

interface ImportReport {
  created: number;
  errors: string[];
  trade_ids: number[];
}

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [report, setReport] = useState<ImportReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImport = async (dryRun: boolean) => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_BASE_URL}/trades/import?dry_run=${dryRun}`, {
      method: "POST",
      body: formData,
      credentials: "include"
    });
    if (!response.ok) {
      setError(await response.text());
      return;
    }
    setReport(await response.json());
    setError(null);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Import trades</h2>
      <Card>
        <div className="space-y-3">
          <p className="text-sm text-slate-300">Upload your trade CSV to preview and confirm the import.</p>
          <Input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          <div className="flex gap-3">
            <Button type="button" onClick={() => handleImport(true)}>
              Preview import
            </Button>
            <Button type="button" onClick={() => handleImport(false)}>
              Commit import
            </Button>
            <a className="rounded-md border border-slate-700 px-4 py-2 text-sm" href={`${API_BASE_URL}/templates/trades.csv`}>
              Download template
            </a>
          </div>
          {error ? <p className="text-sm text-rose-400">{error}</p> : null}
        </div>
      </Card>
      {report ? (
        <Card>
          <h3 className="mb-2 text-lg font-semibold">Import summary</h3>
          <p className="text-sm text-slate-300">Trades processed: {report.created}</p>
          {report.errors.length ? (
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-rose-300">
              {report.errors.map((err, idx) => (
                <li key={idx}>{err}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-emerald-300">No errors detected.</p>
          )}
        </Card>
      ) : null}
    </div>
  );
}
