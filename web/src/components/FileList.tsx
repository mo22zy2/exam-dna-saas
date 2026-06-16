"use client";

interface FileItem {
  file_id: string;
  filename: string;
  file_size: number;
  classification: string;
  created_at: string;
  validation_status?: string;
}

interface FileListProps {
  files: FileItem[];
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileList({ files }: FileListProps) {
  if (files.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p>No files uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-gray-700">Uploaded Files</h3>
      <ul className="space-y-2">
        {files.map((f) => (
          <li
            key={f.file_id}
            className="flex items-center gap-3 bg-white border rounded-lg p-3"
          >
            <span className="flex-1 truncate text-sm font-medium">
              {f.filename}
            </span>
            <span className="text-xs text-gray-400">{formatSize(f.file_size)}</span>
            <span
              className={`text-xs font-medium px-2 py-0.5 rounded ${
                f.classification === "exam"
                  ? "bg-purple-100 text-purple-700"
                  : "bg-orange-100 text-orange-700"
              }`}
            >
              {f.classification === "exam" ? "Exam" : "Lecture"}
            </span>
            {f.validation_status && (
              <span
                className={`text-xs font-medium px-2 py-0.5 rounded ${
                  f.validation_status === "validated"
                    ? "bg-green-100 text-green-700"
                    : f.validation_status === "rejected"
                    ? "bg-red-100 text-red-700"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {f.validation_status}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
