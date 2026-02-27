export default function Loading() {
  return (
    <div className="min-h-screen bg-bg flex items-center justify-center" role="status" aria-label="Loading">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-accent/30 border-t-accent animate-spin" />
        <p className="text-muted text-sm animate-pulse">Loading...</p>
      </div>
    </div>
  );
}
