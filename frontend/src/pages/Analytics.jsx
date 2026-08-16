import { useEffect, useState } from 'react';
import { Card, CardHeader, CardBody, StatCard, SkeletonCard, ErrorState } from '../components/ui';
import { ThreatTrendChart, ThreatCategoryChart } from '../components/charts';
import { fetchAnalytics } from '../services/analyticsService';
import { Percent, TrendingUp, ShieldAlert } from 'lucide-react';

export default function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchAnalytics()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || 'Failed to load analytics.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const detectionRate =
    data && data.summary.totalScans > 0
      ? Math.round((data.summary.threatsDetected / data.summary.totalScans) * 100)
      : 0;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-primary">Analytics</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Aggregate trends across all of your scans.
        </p>
      </div>

      {error && <ErrorState title="Couldn't load analytics" description={error} />}

      {loading && !error && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {!loading && !error && data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard icon={Percent} label="Detection rate" value={`${detectionRate}%`} />
            <StatCard icon={TrendingUp} label="Total scans" value={data.summary.totalScans} />
            <StatCard icon={ShieldAlert} label="Threats detected" value={data.summary.threatsDetected} />
          </div>

          <Card>
            <CardHeader title="Threat trend" subtitle="Verdict distribution over the last 8 days" />
            <CardBody>
              <ThreatTrendChart data={data.threatTrend} />
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Classification breakdown" subtitle="Scans by risk level" />
            <CardBody>
              <ThreatCategoryChart data={data.classificationBreakdown} />
            </CardBody>
          </Card>
        </>
      )}
    </div>
  );
}