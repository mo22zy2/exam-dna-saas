"use client";

import ProtectedLayout from "@/components/ProtectedLayout";
import { useAuth } from "@/lib/auth";

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <ProtectedLayout>
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
          <h1 className="text-2xl font-bold mb-6 text-center">Profile</h1>
          {user && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-500">Email</label>
                <p className="text-gray-900">{user.email}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Plan</label>
                <span className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-700 mt-1">
                  {user.plan === "free" ? "Free Plan" : "Pro Plan"}
                </span>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Member since</label>
                <p className="text-gray-900">
                  {new Date(user.created_at).toLocaleDateString()}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Analyses this month</label>
                <p className="text-gray-900">{user.analyses_used_this_month}</p>
              </div>
              {user.is_admin && (
                <div>
                  <span className="inline-flex items-center rounded-full bg-purple-100 px-3 py-1 text-sm font-medium text-purple-700">
                    Admin
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </ProtectedLayout>
  );
}
