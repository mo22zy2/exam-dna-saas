const API_BASE = "http://localhost:8000";
const MAX_FILE_SIZE = 50 * 1024 * 1024;

export interface UploadSession {
  session_id: string;
  status: string;
  file_count: number;
  max_files: number;
}

export interface FileDetail {
  file_id: string;
  filename: string;
  file_size: number;
  classification: string;
  status: string;
  progress: number;
}

export interface SessionStatus {
  session_id: string;
  status: string;
  files: FileDetail[];
}

export interface FileItem {
  file_id: string;
  filename: string;
  file_size: number;
  classification: string;
  status?: string;
  validation_status?: string;
  session_id?: string;
  created_at: string;
}

export interface FileListData {
  files: FileItem[];
  total_count: number;
  plan_limit: number;
}

export interface UsageLimit {
  files_uploaded: number;
  plan_limit: number;
  analyses_used?: number;
  analyses_limit?: number;
}

export interface PresignedUrlData {
  presigned_url: string;
  file_id: string;
  session_id: string;
  expires_in_seconds: number;
}

export interface UploadFileInfo {
  file: File;
  classification: "exam" | "lecture";
  clientUploadId: string;
  progress: number;
  status: "pending" | "uploading" | "completed" | "failed";
  error?: string;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...init,
  });
  const body = await res.json();
  if (!res.ok) {
    const detail = body.detail || body.error || { message: "Request failed" };
    const message = typeof detail === "string" ? detail : detail.message;
    throw new Error(message);
  }
  return body.data || body;
}

export async function createSession(): Promise<UploadSession> {
  return apiFetch("/upload/session", { method: "POST" });
}

export async function requestPresignedUrl(
  filename: string,
  fileSize: number,
  classification: string,
): Promise<PresignedUrlData> {
  const data = await apiFetch<PresignedUrlData>("/upload/presign-url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename, file_size: fileSize, classification }),
  });
  return data;
}

export async function uploadToR2(
  presignedUrl: string,
  file: File,
  onProgress?: (pct: number) => void,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", presignedUrl);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve();
      } else if (xhr.status === 403) {
        reject(new Error("PRESIGNED_URL_EXPIRED"));
      } else {
        reject(new Error(`Upload failed with status ${xhr.status}`));
      }
    };

    xhr.onerror = () => reject(new Error("Network error"));

    xhr.setRequestHeader("Content-Type", "application/pdf");
    xhr.send(file);
  });
}

export async function completeUpload(fileId: string): Promise<{ file_id: string; status: string; validation_status: string }> {
  return apiFetch(`/upload/${fileId}/complete`, { method: "POST" });
}

export async function uploadFileViaPresignedUrl(
  file: File,
  classification: string,
  onProgress?: (pct: number) => void,
): Promise<{ file_id: string }> {
  if (file.size > MAX_FILE_SIZE) {
    throw new Error(`File exceeds 50 MB limit`);
  }

  const { presigned_url, file_id } = await requestPresignedUrl(
    file.name,
    file.size,
    classification,
  );

  await uploadToR2(presigned_url, file, onProgress);

  await completeUpload(file_id);

  return { file_id };
}

export async function uploadFile(
  sessionId: string,
  file: File,
  classification: string,
  onProgress?: (pct: number) => void
): Promise<{ file_id: string }> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/upload/${sessionId}/files`);
    xhr.withCredentials = true;

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      try {
        const body = JSON.parse(xhr.responseText);
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(body.data || body);
        } else {
          const detail = body.detail || body.error || {};
          reject(new Error(detail.message || "Upload failed"));
        }
      } catch {
        reject(new Error("Upload failed"));
      }
    };

    xhr.onerror = () => reject(new Error("Network error"));

    const formData = new FormData();
    formData.append("file", file);
    formData.append("classification", classification);
    xhr.send(formData);
  });
}

export async function getSessionStatus(sessionId: string): Promise<SessionStatus> {
  return apiFetch(`/upload/session/${sessionId}`);
}

export async function listFiles(): Promise<FileListData> {
  return apiFetch("/upload/files");
}

export async function getUsageLimits(): Promise<UsageLimit> {
  return apiFetch("/upload/limits");
}
