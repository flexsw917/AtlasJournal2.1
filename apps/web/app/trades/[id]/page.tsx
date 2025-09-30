"use client";

import { useParams, useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { Button, Card, Input, Textarea } from "@/components/ui";
import { API_BASE_URL, apiFetch } from "@/lib/api";

interface Tag {
  id: number;
  name: string;
}

interface JournalEntry {
  id: number;
  body: string;
  created_at: string;
}

interface Attachment {
  id: number;
  filename: string;
  size: number;
  uploaded_at: string;
}

interface TradeDetail {
  id: number;
  instrument: { symbol: string };
  direction: string;
  status: string;
  strategy?: string;
  net_pl: number;
  fees: number;
  notes?: string;
  opened_at: string;
  closed_at?: string;
  executions: { id: number; side: string; qty: number; price: number; timestamp: string }[];
  journal_entries: JournalEntry[];
  tags: Tag[];
  attachments: Attachment[];
}

export default function TradeDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [trade, setTrade] = useState<TradeDetail | null>(null);
  const [tags, setTags] = useState<Tag[]>([]);
  const [selectedTags, setSelectedTags] = useState<number[]>([]);
  const [journalBody, setJournalBody] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const tradeId = Number(params.id);

  useEffect(() => {
    async function load() {
      try {
        const [tradeResponse, tagResponse] = await Promise.all([
          apiFetch<TradeDetail>(`/trades/${tradeId}`),
          apiFetch<Tag[]>("/tags/")
        ]);
        setTrade(tradeResponse);
        setTags(tagResponse);
        setSelectedTags(tradeResponse.tags.map((tag) => tag.id));
      } catch (err) {
        setError((err as Error).message);
      }
    }

    load();
  }, [tradeId]);

  const refreshTrade = async () => {
    const updated = await apiFetch<TradeDetail>(`/trades/${tradeId}`);
    setTrade(updated);
    setSelectedTags(updated.tags.map((tag) => tag.id));
  };

  const handleTagUpdate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await apiFetch(`/trades/${tradeId}/tags`, {
      method: "POST",
      body: JSON.stringify({ tag_ids: selectedTags })
    });
    await refreshTrade();
  };

  const handleAddJournal = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!journalBody.trim()) return;
    await apiFetch(`/trades/${tradeId}/journal`, {
      method: "POST",
      body: JSON.stringify({ body: journalBody })
    });
    setJournalBody("");
    await refreshTrade();
  };

  const handleUpload = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const response = await fetch(`${API_BASE_URL}/trades/${tradeId}/attachments`, {
      method: "POST",
      body: formData,
      credentials: "include"
    });
    if (!response.ok) {
      setError(await response.text());
      return;
    }
    setFile(null);
    await refreshTrade();
  };

  if (!trade) {
    return <p className="text-sm text-slate-400">Loading trade...</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Trade {trade.instrument.symbol}</h2>
        <Button onClick={() => router.push("/trades")}>Back to trades</Button>
      </div>
      {error ? <p className="text-sm text-rose-400">{error}</p> : null}
      <Card>
        <h3 className="text-lg font-semibold">Overview</h3>
        <p className="mt-2 text-sm text-slate-300">Status: {trade.status}</p>
        <p className="text-sm text-slate-300">Direction: {trade.direction}</p>
        <p className="text-sm text-slate-300">Net P/L: ${trade.net_pl.toFixed(2)}</p>
        <p className="text-sm text-slate-300">Fees: ${trade.fees.toFixed(2)}</p>
        <p className="text-sm text-slate-300">Strategy: {trade.strategy ?? "—"}</p>
        <p className="text-sm text-slate-300">Notes: {trade.notes ?? "—"}</p>
      </Card>

      <Card>
        <h3 className="mb-4 text-lg font-semibold">Tags</h3>
        <form className="space-y-3" onSubmit={handleTagUpdate}>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <label key={tag.id} className="flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1">
                <input
                  type="checkbox"
                  checked={selectedTags.includes(tag.id)}
                  onChange={(event) => {
                    setSelectedTags((current) =>
                      event.target.checked ? [...current, tag.id] : current.filter((id) => id !== tag.id)
                    );
                  }}
                />
                <span className="text-sm">{tag.name}</span>
              </label>
            ))}
          </div>
          <Button type="submit">Update tags</Button>
        </form>
      </Card>

      <Card>
        <h3 className="mb-4 text-lg font-semibold">Journal</h3>
        <form className="space-y-3" onSubmit={handleAddJournal}>
          <Textarea value={journalBody} onChange={(event) => setJournalBody(event.target.value)} rows={4} />
          <Button type="submit">Add note</Button>
        </form>
        <div className="mt-4 space-y-3">
          {trade.journal_entries.map((entry) => (
            <div key={entry.id} className="rounded-md border border-slate-800 bg-slate-900/70 p-3 text-sm">
              <p className="text-slate-200">{entry.body}</p>
              <p className="text-xs text-slate-500">{new Date(entry.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h3 className="mb-4 text-lg font-semibold">Attachments</h3>
        <form className="flex flex-wrap items-center gap-3" onSubmit={handleUpload}>
          <Input type="file" onChange={(event) => setFile(event.target.files?.[0] ?? null)} />
          <Button type="submit">Upload</Button>
        </form>
        <ul className="mt-4 space-y-2 text-sm text-slate-300">
          {trade.attachments.map((attachment) => (
            <li key={attachment.id} className="flex items-center justify-between">
              <span>
                {attachment.filename} ({(attachment.size / 1024).toFixed(1)} KB)
              </span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
