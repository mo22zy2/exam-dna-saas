"use client";

import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth";

export default function Header() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  if (loading) {
    return (
      <header className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-6xl flex items-center justify-between px-4 py-3">
          <span className="text-lg font-bold text-gray-900">Exam DNA</span>
        </div>
      </header>
    );
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-6xl flex items-center justify-between px-4 py-3">
        <a href="/" className="text-lg font-bold text-gray-900">
          Exam DNA
        </a>
        {user && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user.email}</span>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:underline"
            >
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
