// Maps the real backend's scan/history shapes (risk_score, 5-tier
// classification, created_at, reasons/positive_signals/negative_signals)
// into the shape the existing Module 1 UI components already expect
// (score, level, scannedAt, factors). Centralizing this here means
// none of the existing UI components had to change for Module 5.

import { levelFromScore } from './risk';

export function mapScanSummary(item) {
  return {
    id: item.id,
    url: item.url,
    score: item.risk_score,
    level: levelFromScore(item.risk_score),
    scannedAt: item.created_at,
  };
}

export function mapScanDetail(item) {
  const factors = [
    ...(item.negative_signals || []).map((label) => ({ label, positive: false })),
    ...(item.positive_signals || []).map((label) => ({ label, positive: true })),
  ];
  return {
    ...mapScanSummary(item),
    factors,
    classification: item.classification,
    confidence: item.confidence,
    domainAnalysis: item.domain_analysis,
    dnsAnalysis: item.dns_analysis,
    sslAnalysis: item.ssl_analysis,
    threatIntelligence: item.threat_intelligence,
  };
}