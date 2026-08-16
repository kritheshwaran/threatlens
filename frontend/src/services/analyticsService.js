import { apiFetch } from './api';
import { mapScanSummary } from '../utils/mapScan';

/**
 * Maps the backend's snake_case analytics payload into the camelCase
 * shape the existing Module 1 Dashboard/Analytics components expect
 * (SummaryStats, ThreatTrendChart, ThreatCategoryChart, RecentScansTable).
 */
export async function fetchAnalytics() {
  const data = await apiFetch('/analytics/');
  return {
    summary: {
      totalScans: data.summary.total_scans,
      safeUrls: data.summary.safe_scans,
      threatsDetected: data.summary.threats_detected,
      scansToday: data.summary.scans_today,
      changeVsYesterday: data.summary.change_vs_yesterday,
    },
    threatTrend: data.threat_trend,
    classificationBreakdown: data.classification_breakdown,
    recentScans: data.recent_scans.map(mapScanSummary),
  };
}