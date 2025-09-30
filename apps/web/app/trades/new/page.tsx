"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";

import { Button, Card, Input, Textarea } from "@/components/ui";
import { apiFetch } from "@/lib/api";

const executionSchema = z.object({
  side: z.enum(["buy", "sell"]),
  qty: z.coerce.number().positive(),
  price: z.coerce.number().positive(),
  timestamp: z.string()
});

const schema = z.object({
  symbol: z.string().min(1),
  direction: z.enum(["long", "short"]),
  strategy: z.string().optional(),
  opened_at: z.string(),
  closed_at: z.string().optional(),
  notes: z.string().optional(),
  fees: z.coerce.number().min(0),
  executions: z.array(executionSchema).min(1)
});

type FormValues = z.infer<typeof schema>;

export default function NewTradePage() {
  const router = useRouter();
  const {
    control,
    register,
    handleSubmit,
    formState: { isSubmitting }
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      direction: "long",
      executions: [
        {
          side: "buy",
          qty: 1,
          price: 0,
          timestamp: new Date().toISOString().slice(0, 16)
        }
      ]
    }
  });
  const { fields, append, remove } = useFieldArray({ control, name: "executions" });

  const onSubmit = async (values: FormValues) => {
    await apiFetch("/trades/", {
      method: "POST",
      body: JSON.stringify({
        instrument: { symbol: values.symbol, asset_type: "equity" },
        direction: values.direction,
        strategy: values.strategy,
        opened_at: values.opened_at,
        closed_at: values.closed_at,
        fees: values.fees,
        notes: values.notes,
        executions: values.executions.map((execution) => ({
          ...execution,
          qty: Number(execution.qty),
          price: Number(execution.price)
        }))
      })
    });
    router.push("/trades");
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">New trade</h2>
      <Card>
        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm">
              Symbol
              <Input placeholder="AAPL" {...register("symbol")} />
            </label>
            <label className="text-sm">
              Direction
              <select
                className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                {...register("direction")}
              >
                <option value="long">Long</option>
                <option value="short">Short</option>
              </select>
            </label>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="text-sm">
              Opened at
              <Input type="datetime-local" {...register("opened_at")} />
            </label>
            <label className="text-sm">
              Closed at
              <Input type="datetime-local" {...register("closed_at")} />
            </label>
          </div>
          <label className="text-sm">
            Strategy
            <Input placeholder="Playbook name" {...register("strategy")} />
          </label>
          <label className="text-sm">
            Notes
            <Textarea rows={3} placeholder="Why did you take this trade?" {...register("notes")} />
          </label>
          <label className="text-sm">
            Fees
            <Input type="number" step="0.01" {...register("fees", { valueAsNumber: true })} />
          </label>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Executions</h3>
              <Button
                type="button"
                onClick={() =>
                  append({
                    side: "sell",
                    qty: 1,
                    price: 0,
                    timestamp: new Date().toISOString().slice(0, 16)
                  })
                }
              >
                Add execution
              </Button>
            </div>
            <div className="space-y-3">
              {fields.map((field, index) => (
                <div key={field.id} className="grid gap-3 sm:grid-cols-5">
                  <label className="text-sm">
                    Side
                    <select
                      className="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
                      {...register(`executions.${index}.side` as const)}
                    >
                      <option value="buy">Buy</option>
                      <option value="sell">Sell</option>
                    </select>
                  </label>
                  <label className="text-sm">
                    Qty
                    <Input type="number" step="0.01" {...register(`executions.${index}.qty` as const)} />
                  </label>
                  <label className="text-sm">
                    Price
                    <Input type="number" step="0.01" {...register(`executions.${index}.price` as const)} />
                  </label>
                  <label className="text-sm sm:col-span-2">
                    Timestamp
                    <Input type="datetime-local" {...register(`executions.${index}.timestamp` as const)} />
                  </label>
                  {fields.length > 1 ? (
                    <Button type="button" className="sm:col-span-5" onClick={() => remove(index)}>
                      Remove
                    </Button>
                  ) : null}
                </div>
              ))}
            </div>
          </div>

          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? "Saving..." : "Create trade"}
          </Button>
        </form>
      </Card>
    </div>
  );
}
