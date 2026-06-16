"use client";

interface UsageLimitBadgeProps {
  filesUploaded: number;
  planLimit: number;
  analysesUsed?: number;
  analysesLimit?: number;
}

export default function UsageLimitBadge({
  filesUploaded,
  planLimit,
  analysesUsed,
  analysesLimit,
}: UsageLimitBadgeProps) {
  const fileRemaining = Math.max(0, planLimit - filesUploaded);
  const analysisRemaining = analysesLimit != null && analysesUsed != null
    ? Math.max(0, analysesLimit - analysesUsed)
    : null;

  return (
    <div className="text-sm text-gray-600 space-y-0.5">
      <div>
        <span className="font-medium">{filesUploaded}</span>
        {" of "}
        <span className="font-medium">{planLimit}</span>
        {" files used"}
        {fileRemaining > 0 && (
          <span className="text-gray-400 ml-1">({fileRemaining} remaining)</span>
        )}
        {fileRemaining === 0 && (
          <span className="text-amber-600 ml-1 font-medium">— limit reached</span>
        )}
      </div>
      {analysisRemaining != null && (
        <div>
          <span className="font-medium">{analysesUsed}</span>
          {" of "}
          <span className="font-medium">{analysesLimit}</span>
          {" analysis this month"}
          {analysisRemaining > 0 && (
            <span className="text-gray-400 ml-1">({analysisRemaining} remaining)</span>
          )}
          {analysisRemaining === 0 && (
            <span className="text-amber-600 ml-1 font-medium">— quota exhausted</span>
          )}
        </div>
      )}
    </div>
  );
}
