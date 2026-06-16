"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface FileEntry {
  id: string;
  file: File;
  classification: "exam" | "lecture" | null;
}

interface FileDropzoneProps {
  files: FileEntry[];
  onFilesAdded: (entries: FileEntry[]) => void;
  onFileRemoved: (id: string) => void;
  onClassificationChanged: (id: string, classification: "exam" | "lecture") => void;
  disabled?: boolean;
}

const MAX_SIZE = 50 * 1024 * 1024;

export default function FileDropzone({
  files,
  onFilesAdded,
  onFileRemoved,
  onClassificationChanged,
  disabled,
}: FileDropzoneProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      const entries: FileEntry[] = accepted.map((f) => ({
        id: crypto.randomUUID(),
        file: f,
        classification: null,
      }));
      const total = files.length + entries.length;
      const capped = total > 10 ? entries.slice(0, 10 - files.length) : entries;
      if (capped.length < entries.length) {
        alert("Maximum 10 files per batch. Extra files were ignored.");
      }
      onFilesAdded(capped);
    },
    [files.length, onFilesAdded]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize: MAX_SIZE,
    maxFiles: 10,
    disabled,
    onDropRejected: (rejections) => {
      for (const r of rejections) {
        for (const err of r.errors) {
          if (err.code === "file-too-large") {
            alert(`${r.file.name} exceeds 50 MB limit.`);
          } else if (err.code === "file-invalid-type") {
            alert(`${r.file.name} is not a PDF file.`);
          } else {
            alert(`${r.file.name}: ${err.message}`);
          }
        }
      }
    },
    validator: (file) => {
      if (file.size > MAX_SIZE) {
        return { code: "file-too-large", message: "File exceeds 50 MB" };
      }
      return null;
    },
  });

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p className="text-blue-600">Drop PDF files here...</p>
        ) : (
          <div>
            <p className="text-gray-600">Drag & drop PDF files here, or click to select</p>
            <p className="text-sm text-gray-400 mt-1">Max 50 MB per file, PDF only</p>
          </div>
        )}
      </div>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((entry) => (
            <li
              key={entry.id}
              className="flex items-center gap-3 bg-gray-50 rounded-lg p-3"
            >
              <span className="flex-1 truncate text-sm font-medium">
                {entry.file.name}
              </span>
              <span className="text-xs text-gray-400">
                {formatSize(entry.file.size)}
              </span>
              <select
                value={entry.classification || ""}
                onChange={(e) =>
                  onClassificationChanged(
                    entry.id,
                    e.target.value as "exam" | "lecture"
                  )
                }
                className="text-sm border rounded px-2 py-1"
                disabled={disabled}
              >
                <option value="" disabled>
                  Tag...
                </option>
                <option value="exam">Exam</option>
                <option value="lecture">Lecture</option>
              </select>
              <button
                onClick={() => onFileRemoved(entry.id)}
                className="text-red-500 hover:text-red-700 text-sm font-medium"
                disabled={disabled}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
