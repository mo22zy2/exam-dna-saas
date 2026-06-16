"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function Home() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (user) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-indigo-900">Exam DNA</h1>
          <div className="flex items-center gap-6">
            <Link href="/profile" className="text-sm font-medium text-gray-700 hover:text-indigo-600">
              Profile
            </Link>
            <button
              onClick={() => logout()}
              className="text-sm font-medium text-red-600 hover:text-red-700"
            >
              Sign Out
            </button>
          </div>
        </header>

        <main className="flex-1 p-8">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Welcome back, {user.email}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">My Files</h3>
                <p className="text-gray-500 text-sm mb-4">View and manage your uploaded exams.</p>
                <div className="text-indigo-600 font-medium text-sm">
                  Available in Dashboard →
                </div>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload</h3>
                <p className="text-gray-500 text-sm mb-4">Analyze a new exam or lecture note.</p>
                <div className="text-indigo-600 font-medium text-sm">
                  PDF Analysis Ready →
                </div>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Plan</h3>
                <p className="text-gray-500 text-sm mb-4">You are currently on the {user.plan} plan.</p>
                <Link href="/profile" className="text-indigo-600 font-medium text-sm hover:underline">
                  Manage Plan →
                </Link>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="flex flex-col items-center gap-8 px-8">
        <h1 className="text-5xl font-bold tracking-tight text-indigo-900">
          Exam DNA
        </h1>
        <p className="text-lg text-indigo-700/80 max-w-md text-center">
          SaaS platform for exam analysis and insights. Get detailed breakdown of your exam results.
        </p>
        <div className="flex gap-4">
          <Link
            href="/login"
            className="bg-indigo-600 text-white px-8 py-3 rounded-full font-semibold hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200"
          >
            Get Started
          </Link>
          <Link
            href="/register"
            className="bg-white text-indigo-600 px-8 py-3 rounded-full font-semibold border border-indigo-200 hover:bg-indigo-50 transition-colors"
          >
            Sign Up
          </Link>
        </div>
      </main>
    </div>
  );
}
