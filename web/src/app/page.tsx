export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <main className="flex flex-col items-center gap-8 px-8">
        <h1 className="text-5xl font-bold tracking-tight text-indigo-900">
          Exam DNA
        </h1>
        <p className="text-lg text-indigo-700/80 max-w-md text-center">
          SaaS platform for exam analysis and insights
        </p>
        <div className="flex gap-4">
          <div className="rounded-xl border border-indigo-200 bg-white/60 px-6 py-4 text-sm text-indigo-600 shadow-sm">
            API: <code className="font-mono text-indigo-800">localhost:8000</code>
          </div>
          <div className="rounded-xl border border-indigo-200 bg-white/60 px-6 py-4 text-sm text-indigo-600 shadow-sm">
            Status:{" "}
            <span className="inline-flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              Running
            </span>
          </div>
        </div>
      </main>
    </div>
  );
}
