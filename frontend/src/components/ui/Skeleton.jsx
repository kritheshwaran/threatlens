export function Skeleton({ className = '' }) {
  return <div className={`animate-pulse rounded-md bg-surface2 ${className}`} />;
}

export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <Skeleton className="h-3 w-24" />
      <Skeleton className="mt-4 h-7 w-16" />
    </div>
  );
}

export function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 border-b border-border px-5 py-4">
      <Skeleton className="h-3 w-1/3" />
      <Skeleton className="h-3 w-16" />
      <Skeleton className="ml-auto h-3 w-20" />
    </div>
  );
}