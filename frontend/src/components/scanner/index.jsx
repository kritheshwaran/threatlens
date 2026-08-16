import { useState } from 'react';
import { ScanLine, Search } from 'lucide-react';
import { Card, CardBody, Button, RiskGauge, RiskBadge, ErrorState } from '../ui';
import { riskMeta, formatScore } from '../../utils/risk';

export function ScanForm({ onSubmit, loading }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!url.trim()) return;
    onSubmit(url.trim());
  };

  return (
    <Card>
      <CardBody>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search
              size={16}
              className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-text-muted"
            />
            <input
              type="text"
              inputMode="url"
              placeholder="Enter a URL to scan, e.g. https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
              className="h-11 w-full rounded-lg border border-border bg-surface2 pl-10 pr-3 font-mono text-sm
                text-text-primary placeholder:text-text-muted placeholder:font-body
                focus:border-accent focus:outline-none disabled:opacity-60"
            />
            {loading && (
              <span className="absolute inset-y-0 right-0 flex w-24 items-center overflow-hidden rounded-r-lg">
                <span className="h-full w-8 animate-scanline bg-gradient-to-r from-transparent via-accent/30 to-transparent" />
              </span>
            )}
          </div>
          <Button type="submit" disabled={loading || !url.trim()} className="sm:w-40">
            <ScanLine size={16} strokeWidth={2.25} />
            {loading ? 'Scanning…' : 'Scan URL'}
          </Button>
        </form>
      </CardBody>
    </Card>
  );
}

export function ScanResultPanel({ status, result, error, onReset }) {
  if (status === 'idle') {
    return (
      <Card className="flex flex-col items-center justify-center gap-3 py-16 text-center">
        <span className="flex h-11 w-11 items-center justify-center rounded-full bg-surface2 text-text-secondary">
          <ScanLine size={20} strokeWidth={1.75} />
        </span>
        <div>
          <p className="font-display text-sm font-semibold text-text-primary">
            No scan yet
          </p>
          <p className="mt-1 max-w-sm text-sm text-text-secondary">
            Enter a URL above to see its risk score, verdict, and the signals behind it.
          </p>
        </div>
      </Card>
    );
  }

  if (status === 'loading') {
    return (
      <Card className="flex flex-col items-center justify-center gap-4 py-14">
        <RiskGauge scanning size={140} />
        <p className="text-sm text-text-secondary">Analyzing signals…</p>
      </Card>
    );
  }

  if (status === 'error') {
    return (
      <ErrorState
        title="Scan failed"
        description={error}
        action={
          <Button variant="secondary" size="sm" onClick={onReset}>
            Try again
          </Button>
        }
      />
    );
  }

  if (status === 'success' && result) {
    const meta = riskMeta(result.level);
    return (
      <Card>
        <CardBody className="flex flex-col items-center gap-5 py-8 text-center sm:flex-row sm:items-center sm:text-left">
          <RiskGauge score={result.score} level={result.level} size={140} />
          <div className="flex-1">
            <div className="flex flex-wrap items-center justify-center gap-2 sm:justify-start">
              <RiskBadge level={result.level} />
              <span className="font-mono text-xs text-text-muted">
                {new Date(result.scannedAt).toLocaleString()}
              </span>
            </div>
            <p className="mt-2 break-all font-mono text-sm text-text-primary">{result.url}</p>
            <p className="mt-1 text-sm text-text-secondary">{meta.description}</p>

            <ul className="mt-4 space-y-1.5 text-left">
              {result.factors.map((factor) => (
                <li key={factor.label} className="flex items-center gap-2 text-sm">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      factor.positive ? 'bg-safe' : 'bg-malicious'
                    }`}
                  />
                  <span className={factor.positive ? 'text-text-secondary' : 'text-text-primary'}>
                    {factor.label}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </CardBody>
      </Card>
    );
  }

  return null;
}

export function scoreLabel(score) {
  return `${formatScore(score)} / 100`;
}