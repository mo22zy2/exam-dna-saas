"use client";

interface QueueFile {
  id: string;
  filename: string;
  status: "pending" | "uploading" | "completed" | "failed";
  progress: number;
  error?: string;
}

interface UploadQueueProps {
  files: QueueFile[];
}

export default function UploadQueue({ files }: UploadQueueProps) {
  if (files.length === 0) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-700">Upload Queue</h3>
      <ul className="space-y-2">
        {files.map((f) => (
          <li key={f.id} className="bg-white border rounded-lg p-3 space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium truncate flex-1">
                {f.filename}
              </span>
              <StatusBadge status={f.status} />
            </div>
            {(f.status === "uploading" || f.status === "completed") && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    f.status === "completed" ? "bg-green-500" : "bg-blue-500"
                  }`}
                  style={{ width: `${f.progress}%` }}
                />
              </div>
            )}
            {f.status === "uploading" && (
              <p className="text-xs text-gray-400">{f.progress}%</p>
            )}
            {f.error && (
              <p className="text-xs text-red-500">{f.error}</p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

function StatusBadge({ status }: { status: QueueFile["status"] }) {
  const styles: Record<string, string> = {
    pending: "bg-gray-100 text-gray-600",
    uploading: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    failed: "bg-red-100 text-red-700",
  };

  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded ${styles[status]}`}>
      {status}
    </span>
  );
}
