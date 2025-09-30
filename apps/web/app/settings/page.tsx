"use client";

import { useEffect, useState } from "react";

import { Button, Card } from "@/components/ui";
import { apiFetch } from "@/lib/api";

type Profile = {
  email: string;
  created_at: string;
};

export default function SettingsPage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<Profile>("/me")
      .then(setProfile)
      .catch((err) => setError((err as Error).message));
  }, []);

  const handleLogout = async () => {
    await apiFetch("/auth/logout", { method: "POST", parseJson: false });
    window.location.href = "/login";
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Settings</h2>
      <Card>
        <h3 className="text-lg font-semibold">Profile</h3>
        {profile ? (
          <div className="mt-3 space-y-2 text-sm text-slate-300">
            <p>Email: {profile.email}</p>
            <p>Joined: {new Date(profile.created_at).toLocaleDateString()}</p>
          </div>
        ) : (
          <p className="text-sm text-slate-400">{error ?? "Loading profile..."}</p>
        )}
        <Button className="mt-4" onClick={handleLogout}>
          Log out
        </Button>
      </Card>
      <Card>
        <h3 className="text-lg font-semibold">API token</h3>
        <p className="mt-2 text-sm text-slate-300">Coming soon. Generate personal tokens for automation workflows.</p>
      </Card>
    </div>
  );
}
