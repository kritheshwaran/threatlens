import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Globe, Clock, ShieldQuestion } from 'lucide-react';
import { Card, CardHeader, CardBody, RiskGauge, RiskBadge, EmptyState, Button } from '../components/ui';
import { riskMeta } from '../utils/risk';
import { useScanHistory } from '../context/ScanHistoryContext';

export default function Report() {
  const { id } = useParams();
  const { history } = useScanHistory();
  const scan = history.find((s) => s.id === id);

  if (!scan) {
    return (
      <div className="flex flex-col gap-6">
        <Link to="/history" className="flex w-fit items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary">
          <ArrowLeft size={15} /> Back to history
        </Link>
        <EmptyState
          icon={ShieldQuestion}
          title="Report not found"
          description="This scan result doesn't exist or hasn't been run yet."
          action={
            <Link to="/scanner">
              <Button size="sm">Run a new scan</Button>
            </Link>
          }
        />
      </div>
    );
  }

  const meta = riskMeta(scan.level);

  return (
    <div className="flex flex-col gap-6">
      <Link to="/history" className="flex w-fit items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary">
        <ArrowLeft size={15} /> Back to history
      </Link>

      <Card>
        <CardBody className="flex flex-col items-center gap-6 py-10 text-center sm:flex-row sm:items-center sm:text-left">
          <RiskGauge score={scan.score} level={scan.level} size={168} />
          <div className="flex-1">
            <RiskBadge level={scan.level} />
            <p className="mt-3 break-all font-mono text-base text-text-primary">{scan.url}</p>
            <p className="mt-2 text-sm text-text-secondary">{meta.description}</p>
            <div className="mt-4 flex flex-wrap items-center justify-center gap-4 text-xs text-text-muted sm:justify-start">
              <span className="flex items-center gap-1.5">
                <Clock size={13} /> {new Date(scan.scannedAt).toLocaleString()}
              </span>
              <span className="flex items-center gap-1.5">
                <Globe size={13} /> Scan ID: {scan.id}
              </span>
            </div>
          </div>
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Detection signals" subtitle="Factors contributing to this verdict" />
        <div className="divide-y divide-border">
          {scan.factors.map((factor) => (
            <div key={factor.label} className="flex items-center justify-between px-5 py-3.5">
              <span className="text-sm text-text-primary">{factor.label}</span>
              <span
                className={`text-xs font-medium uppercase tracking-wide ${
                  factor.positive ? 'text-safe' : 'text-malicious'
                }`}
              >
                {factor.positive ? 'Positive' : 'Flagged'}
              </span>
            </div>
          ))}
        </div>
      </Card>

      <Card className="border-dashed">
        <CardBody>
          <p className="text-xs text-text-muted">
            This report is generated from mock data as part of Module 1 (frontend foundation).
            Real DNS, SSL, WHOIS, and ML-based analysis will populate these signals in later modules.
          </p>
        </CardBody>
      </Card>
    </div>
  );
}