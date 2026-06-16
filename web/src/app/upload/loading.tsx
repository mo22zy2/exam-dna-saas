export default function UploadLoading() {
  return (
    <div className="max-w-2xl mx-auto py-8 space-y-6 animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-1/3" />
      <div className="h-32 bg-gray-200 rounded-lg" />
      <div className="h-10 bg-gray-200 rounded-lg w-full" />
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded w-1/4" />
        <div className="h-16 bg-gray-200 rounded-lg" />
        <div className="h-16 bg-gray-200 rounded-lg" />
      </div>
    </div>
  );
}
