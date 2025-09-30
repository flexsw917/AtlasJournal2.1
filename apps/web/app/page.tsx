import Link from "next/link";

export default function Home() {
  return (
    <div className="space-y-6 text-center">
      <h2 className="text-3xl font-bold">Welcome to ZellaLite</h2>
      <p className="text-slate-300">Track every trade, learn faster, and iterate on your strategy.</p>
      <div className="flex justify-center gap-4">
        <Link className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-semibold" href="/login">
          Log in
        </Link>
        <Link className="rounded-md border border-emerald-500 px-4 py-2 text-sm font-semibold" href="/signup">
          Sign up
        </Link>
      </div>
    </div>
  );
}
