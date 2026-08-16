import { useEffect, useState } from 'react';
import { Card, CardHeader, CardBody, SkeletonCard, ErrorState } from '../components/ui';
import { SummaryStats, RecentScansTable } from '../components/dashboard';
import { ThreatTrendChart, ThreatCategoryChart } from '../components/charts';
import { fetchAnalytics } from '../services/analyticsService';

export default function Dashboard() {
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
        if (!cancelled) setError(err.message || 'Failed to load dashboard data.');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-primary">Overview</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Threat activity across all scanned URLs.
        </p>
      </div>

      {error && (
        <ErrorState title="Couldn't load dashboard" description={error} />
      )}

      {loading && !error && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {!loading && !error && data && (
        <>
          <SummaryStats summary={data.summary} />

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
            <Card className="xl:col-span-2">
              <CardHeader title="Threat trend" subtitle="Last 8 days by verdict" />
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
          </div>

          <RecentScansTable scans={data.recentScans} />
        </>
      )}
    </div>
  );
}