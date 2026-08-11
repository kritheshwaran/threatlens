import { Link } from 'react-router-dom';
import { ShieldCheck, ShieldAlert, ScanLine, Activity } from 'lucide-react';
import { Card, CardHeader, CardBody, RiskBadge, EmptyState } from '../ui';
import StatCard from '../ui/StatCard';

export function SummaryStats({ summary }) {
  const changePct = Math.round(summary.changeVsYesterday * 100);
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard
        icon={ScanLine}
        label="Total scans"
        value={summary.totalScans.toLocaleString()}
        delta={`+${changePct}% vs yesterday`}
        tone="up"
      />
      <StatCard icon={ShieldCheck} label="Safe URLs" value={summary.safeUrls.toLocaleString()} />
      <StatCard icon={ShieldAlert} label="Threats detected" value={summary.threatsDetected.toLocaleString()} tone="down" />
      <StatCard icon={Activity} label="Scans today" value={summary.scansToday.toLocaleString()} />
    </div>
  );
}

export function RecentScansTable({ scans }) {
  if (!scans || scans.length === 0) {
    return (
      <Card>
        <CardHeader title="Recent scans" />
        <CardBody>
          <EmptyState
            icon={ScanLine}
            title="No scans yet"
            description="Run your first scan to see recent activity here."
          />
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        title="Recent scans"
        action={
          <Link to="/history" className="text-xs font-medium text-accent hover:text-accent-strong">
            View all
          </Link>
        }
      />
      <div className="divide-y divide-border">
        {scans.map((scan) => (
          <Link
            key={scan.id}
            to={`/report/${scan.id}`}
            className="flex items-center gap-4 px-5 py-3.5 transition-colors hover:bg-surface2"
          >
            <span className="min-w-0 flex-1 truncate font-mono text-sm text-text-primary">
              {scan.url}
            </span>
            <span className="hidden font-mono text-xs text-text-muted sm:block">
              {new Date(scan.scannedAt).toLocaleDateString()}
            </span>
            <RiskBadge level={scan.level} size="sm" />
          </Link>
        ))}
      </div>
    </Card>
  );
}