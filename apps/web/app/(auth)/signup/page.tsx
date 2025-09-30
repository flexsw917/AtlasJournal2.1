"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { apiFetch } from "@/lib/api";
import { Button, Card, Input } from "@/components/ui";

const schema = z
  .object({
    email: z.string().email(),
    password: z.string().min(8),
    confirm: z.string().min(8)
  })
  .refine((data) => data.password === data.confirm, {
    message: "Passwords must match",
    path: ["confirm"]
  });

type FormValues = z.infer<typeof schema>;

export default function SignupPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { isSubmitting, errors }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  const onSubmit = async (values: FormValues) => {
    setError(null);
    try {
      await apiFetch("/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email: values.email, password: values.password })
      });
      await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: values.email, password: values.password })
      });
      router.push("/dashboard");
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <Card>
        <h2 className="mb-4 text-xl font-semibold">Create your account</h2>
        <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <label className="block text-sm">
            Email
            <Input type="email" autoComplete="email" {...register("email")} />
          </label>
          <label className="block text-sm">
            Password
            <Input type="password" autoComplete="new-password" {...register("password")} />
          </label>
          <label className="block text-sm">
            Confirm password
            <Input type="password" autoComplete="new-password" {...register("confirm")} />
            {errors.confirm ? <span className="text-xs text-rose-400">{errors.confirm.message}</span> : null}
          </label>
          {error ? <p className="text-sm text-rose-400">{error}</p> : null}
          <Button type="submit" disabled={isSubmitting} className="w-full">
            {isSubmitting ? "Creating..." : "Sign up"}
          </Button>
        </form>
        <p className="mt-4 text-sm text-slate-400">
          Already have an account? <Link href="/login" className="text-emerald-400">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}
