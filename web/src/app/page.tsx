"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/lib/auth";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login");
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-col flex-1 items-center justify-center min-h-[calc(100vh-4rem)] bg-gray-50">
      <main className="flex flex-col items-center gap-6 px-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome, {user.email}
        </h1>
        <div className="flex gap-3">
          <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700">
            {user.plan === "free" ? "Free Plan" : "Pro Plan"}
          </span>
          {user.is_admin && (
            <span className="inline-flex items-center rounded-full bg-purple-100 px-3 py-1 text-sm font-medium text-purple-700">
              Admin
            </span>
          )}
        </div>
        <p className="text-sm text-gray-500">
          Analyses used this month: {user.analyses_used_this_month}
        </p>
      </main>
    </div>
  );
}
