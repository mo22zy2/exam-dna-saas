"use client";

export default function UploadError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md text-center">
        <h2 className="text-lg font-semibold text-red-600 mb-2">
          Something went wrong
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          {error.message || "An unexpected error occurred on the upload page."}
        </p>
        <button
          onClick={reset}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
