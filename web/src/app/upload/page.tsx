"use client";

import { useCallback, useEffect, useState } from "react";
import ProtectedLayout from "@/components/ProtectedLayout";
import FileDropzone from "@/components/FileDropzone";
import FileList from "@/components/FileList";
import UploadQueue from "@/components/UploadQueue";
import UsageLimitBadge from "@/components/UsageLimitBadge";
import {
  listFiles,
  uploadFileViaPresignedUrl,
  getUsageLimits,
  type FileItem,
  type UsageLimit,
} from "@/lib/upload";

interface FileEntry {
  id: string;
  file: File;
  classification: "exam" | "lecture" | null;
}

interface QueueFile {
  id: string;
  filename: string;
  status: "pending" | "uploading" | "completed" | "failed";
  progress: number;
  error?: string;
}

export default function UploadPage() {
  const [selectedFiles, setSelectedFiles] = useState<FileEntry[]>([]);
  const [queue, setQueue] = useState<QueueFile[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<FileItem[]>([]);
  const [usage, setUsage] = useState<UsageLimit | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const refreshData = useCallback(async () => {
    try {
      const [files, limits] = await Promise.all([
        listFiles(),
        getUsageLimits(),
      ]);
      setUploadedFiles(files.files);
      setUsage(limits);
    } catch {
      // silently fail on refresh
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  const handleFilesAdded = (entries: FileEntry[]) => {
    setSelectedFiles((prev) => [...prev, ...entries]);
  };

  const handleFileRemoved = (id: string) => {
    setSelectedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleClassificationChanged = (
    id: string,
    classification: "exam" | "lecture"
  ) => {
    setSelectedFiles((prev) =>
      prev.map((f) => (f.id === id ? { ...f, classification } : f))
    );
  };

  const handleUploadClick = async () => {
    const untagged = selectedFiles.filter((f) => !f.classification);
    if (untagged.length > 0) {
      alert(`Please tag all files as Exam or Lecture before uploading.`);
      return;
    }

    if (selectedFiles.length === 0) {
      alert("No files selected.");
      return;
    }

    setIsUploading(true);

    const queueFiles: QueueFile[] = selectedFiles.map((f) => ({
      id: f.id,
      filename: f.file.name,
      status: "pending" as const,
      progress: 0,
    }));
    setQueue(queueFiles);

    for (let i = 0; i < selectedFiles.length; i++) {
      const entry = selectedFiles[i];

      setQueue((prev) =>
        prev.map((qf) =>
          qf.id === entry.id ? { ...qf, status: "uploading" as const, progress: 0 } : qf
        )
      );

      let attempts = 0;
      const maxAttempts = 2;

      const doUpload = async (): Promise<void> => {
        try {
          await uploadFileViaPresignedUrl(
            entry.file,
            entry.classification!,
            (pct) => {
              setQueue((prev) =>
                prev.map((qf) =>
                  qf.id === entry.id ? { ...qf, progress: pct } : qf
                )
              );
            }
          );

          setQueue((prev) =>
            prev.map((qf) =>
              qf.id === entry.id
                ? { ...qf, status: "completed" as const, progress: 100 }
                : qf
            )
          );
        } catch (err: unknown) {
          if (
            err instanceof Error &&
            err.message === "PRESIGNED_URL_EXPIRED" &&
            attempts < maxAttempts
          ) {
            attempts++;
            await doUpload();
          } else {
            const message = err instanceof Error ? err.message : "Upload failed";
            setQueue((prev) =>
              prev.map((qf) =>
                qf.id === entry.id
                  ? { ...qf, status: "failed" as const, error: message }
                  : qf
              )
            );
          }
        }
      };

      await doUpload();
    }

    setSelectedFiles([]);
    setIsUploading(false);
    refreshData();
  };

  const allTagged = selectedFiles.every((f) => f.classification);
  const canUpload = selectedFiles.length > 0 && allTagged && !isUploading;

  return (
    <ProtectedLayout>
    <div className="max-w-2xl mx-auto py-8 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Upload PDFs</h1>
        {usage && (
          <UsageLimitBadge
            filesUploaded={usage.files_uploaded}
            planLimit={usage.plan_limit}
            analysesUsed={usage.analyses_used}
            analysesLimit={usage.analyses_limit}
          />
        )}
      </div>

      <FileDropzone
        files={selectedFiles}
        onFilesAdded={handleFilesAdded}
        onFileRemoved={handleFileRemoved}
        onClassificationChanged={handleClassificationChanged}
        disabled={isUploading}
      />

      {selectedFiles.length > 0 && (
        <button
          onClick={handleUploadClick}
          disabled={!canUpload}
          className={`w-full py-2 px-4 rounded-lg font-medium text-white transition-colors ${
            canUpload
              ? "bg-blue-600 hover:bg-blue-700"
              : "bg-gray-300 cursor-not-allowed"
          }`}
        >
          {isUploading
            ? "Uploading..."
            : `Upload ${selectedFiles.length} file${selectedFiles.length > 1 ? "s" : ""}`}
        </button>
      )}

      <UploadQueue files={queue} />
      <FileList files={uploadedFiles} />
    </div>
    </ProtectedLayout>
  );
}
