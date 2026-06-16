"use client";

import ProtectedLayout from "@/components/ProtectedLayout";
import { useAuth } from "@/lib/auth";

export default function ProfilePage() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <ProtectedLayout>
      <div className="max-w-2xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-8 text-gray-900">Your Profile</h1>

        <div className="bg-white shadow rounded-lg overflow-hidden border border-gray-200">
          <div className="px-6 py-5 border-b border-gray-200 bg-gray-50">
            <h3 className="text-lg font-medium leading-6 text-gray-900">
              Account Information
            </h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Personal details and subscription plan.
            </p>
          </div>
          <div className="px-6 py-5 space-y-6">
            <div className="grid grid-cols-3 gap-4">
              <dt className="text-sm font-medium text-gray-500">Email address</dt>
              <dd className="text-sm text-gray-900 col-span-2">{user.email}</dd>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <dt className="text-sm font-medium text-gray-500">Plan</dt>
              <dd className="col-span-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                  {user.plan}
                </span>
              </dd>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <dt className="text-sm font-medium text-gray-500">Analyses Used</dt>
              <dd className="text-sm text-gray-900 col-span-2">
                {user.analyses_used_this_month}
              </dd>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <dt className="text-sm font-medium text-gray-500">Account Created</dt>
              <dd className="text-sm text-gray-900 col-span-2">
                {new Date(user.created_at).toLocaleDateString()}
              </dd>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <dt className="text-sm font-medium text-gray-500">Admin Status</dt>
              <dd className="text-sm text-gray-900 col-span-2">
                {user.is_admin ? "Administrator" : "User"}
              </dd>
            </div>
          </div>
        </div>
      </div>
    </ProtectedLayout>
  );
}
