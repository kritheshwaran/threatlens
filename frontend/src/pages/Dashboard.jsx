import { Card, CardHeader, CardBody } from '../components/ui';
import { SummaryStats, RecentScansTable } from '../components/dashboard';
import { ThreatTrendChart, ThreatCategoryChart } from '../components/charts';
import { DASHBOARD_SUMMARY, THREAT_TREND, THREAT_CATEGORY_BREAKDOWN } from '../data/mockData';
import { useScanHistory } from '../context/ScanHistoryContext';

export default function Dashboard() {
  const { history } = useScanHistory();

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-primary">Overview</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Threat activity across all scanned URLs. Data shown is mock data for Module 1.
        </p>
      </div>

      <SummaryStats summary={DASHBOARD_SUMMARY} />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader title="Threat trend" subtitle="Last 8 days by verdict" />
          <CardBody>
            <ThreatTrendChart data={THREAT_TREND} />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Threat categories" subtitle="Share of detected threats" />
          <CardBody>
            <ThreatCategoryChart data={THREAT_CATEGORY_BREAKDOWN} />
          </CardBody>
        </Card>
      </div>

      <RecentScansTable scans={history.slice(0, 5)} />
    </div>
  );
}