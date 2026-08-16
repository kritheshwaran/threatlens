import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, History as HistoryIcon } from 'lucide-react';
import { Card, RiskBadge, EmptyState, ErrorState, SkeletonRow } from '../components/ui';
import { useScanHistory } from '../context/ScanHistoryContext';

const FILTERS = [
  { value: 'all', label: 'All' },
  { value: 'safe', label: 'Safe' },
  { value: 'suspicious', label: 'Suspicious' },
  { value: 'malicious', label: 'Malicious' },
];

export default function History() {
  const { history, loading, error, refresh } = useScanHistory();
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all');

  const filtered = useMemo(() => {
    return history.filter((scan) => {
      const matchesFilter = filter === 'all' || scan.level === filter;
      const matchesQuery = scan.url.toLowerCase().includes(query.toLowerCase());
      return matchesFilter && matchesQuery;
    });
  }, [history, query, filter]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-primary">Scan History</h2>
        <p className="mt-1 text-sm text-text-secondary">All of your scans, most recent first.</p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full sm:max-w-xs">
          <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            placeholder="Filter by URL…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
            className="h-9 w-full rounded-lg border border-border bg-surface2 pl-9 pr-3 text-sm text-text-primary
              placeholder:text-text-muted focus:border-accent focus:outline-none disabled:opacity-60"
          />
        </div>

        <div className="flex gap-1 rounded-lg border border-border bg-surface2 p-1">
          {FILTERS.map((f) => (
            <button
              key={f.value}
              type="button"
              onClick={() => setFilter(f.value)}
              disabled={loading}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-60 ${
                filter === f.value
                  ? 'bg-accent text-white'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <ErrorState
          title="Couldn't load scan history"
          description={error}
          action={
            <button
              type="button"
              onClick={refresh}
              className="text-sm font-medium text-accent hover:text-accent-strong"
            >
              Try again
            </button>
          }
        />
      )}

      {loading && !error && (
        <Card>
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </Card>
      )}

      {!loading && !error && (
        <Card>
          {filtered.length === 0 ? (
            <div className="p-2">
              <EmptyState
                icon={HistoryIcon}
                title={history.length === 0 ? 'No scans yet' : 'No matching scans'}
                description={
                  history.length === 0
                    ? 'Run your first scan to see it appear here.'
                    : 'Try a different search term or filter.'
                }
              />
            </div>
          ) : (
            <div className="divide-y divide-border">
              <div className="hidden grid-cols-[1fr_auto_auto] gap-4 px-5 py-2.5 text-xs font-medium uppercase tracking-wide text-text-muted sm:grid">
                <span>URL</span>
                <span>Scanned</span>
                <span>Verdict</span>
              </div>
              {filtered.map((scan) => (
                <Link
                  key={scan.id}
                  to={`/report/${scan.id}`}
                  className="flex flex-col gap-2 px-5 py-3.5 transition-colors hover:bg-surface2 sm:grid sm:grid-cols-[1fr_auto_auto] sm:items-center sm:gap-4"
                >
                  <span className="min-w-0 truncate font-mono text-sm text-text-primary">{scan.url}</span>
                  <span className="font-mono text-xs text-text-muted">
                    {new Date(scan.scannedAt).toLocaleDateString()}
                  </span>
                  <RiskBadge level={scan.level} size="sm" />
                </Link>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}