import { Card, CardHeader, CardBody, StatCard } from '../components/ui';
import { ThreatTrendChart, ThreatCategoryChart } from '../components/charts';
import { THREAT_TREND, THREAT_CATEGORY_BREAKDOWN, DASHBOARD_SUMMARY } from '../data/mockData';
import { Percent, TrendingDown, Timer } from 'lucide-react';

export default function Analytics() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-primary">Analytics</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Aggregate trends across all scans. Mock data for Module 1.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          icon={Percent}
          label="Detection rate"
          value={`${Math.round(
            (DASHBOARD_SUMMARY.threatsDetected / DASHBOARD_SUMMARY.totalScans) * 100
          )}%`}
        />
        <StatCard icon={TrendingDown} label="Avg. response time" value="1.4s" />
        <StatCard icon={Timer} label="Avg. scans / day" value="183" />
      </div>

      <Card>
        <CardHeader title="Threat trend" subtitle="Verdict distribution over the last 8 days" />
        <CardBody>
          <ThreatTrendChart data={THREAT_TREND} />
        </CardBody>
      </Card>

      <Card>
        <CardHeader title="Threat categories" subtitle="Breakdown of detected threat types" />
        <CardBody>
          <ThreatCategoryChart data={THREAT_CATEGORY_BREAKDOWN} />
        </CardBody>
      </Card>
    </div>
  );
}