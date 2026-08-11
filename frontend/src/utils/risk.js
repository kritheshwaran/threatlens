// Central place that defines what a risk score *means*.
// Thresholds live here only, so the rest of the UI never hardcodes a number.

export const RISK_LEVELS = {
  SAFE: 'safe',
  SUSPICIOUS: 'suspicious',
  MALICIOUS: 'malicious',
};

const LEVEL_META = {
  [RISK_LEVELS.SAFE]: {
    label: 'Safe',
    description: 'No significant threat indicators detected.',
    colorClass: 'text-safe',
    bgClass: 'bg-safe-soft',
    borderClass: 'border-safe/30',
    dotClass: 'bg-safe',
  },
  [RISK_LEVELS.SUSPICIOUS]: {
    label: 'Suspicious',
    description: 'Some indicators warrant caution before proceeding.',
    colorClass: 'text-suspicious',
    bgClass: 'bg-suspicious-soft',
    borderClass: 'border-suspicious/30',
    dotClass: 'bg-suspicious',
  },
  [RISK_LEVELS.MALICIOUS]: {
    label: 'Malicious',
    description: 'Strong indicators of phishing or malicious intent.',
    colorClass: 'text-malicious',
    bgClass: 'bg-malicious-soft',
    borderClass: 'border-malicious/30',
    dotClass: 'bg-malicious',
  },
};

/**
 * Map a 0-100 risk score to a level. Kept as a pure function so the
 * real risk engine (Module 3+) can call the exact same mapping.
 */
export function levelFromScore(score) {
  if (score >= 70) return RISK_LEVELS.MALICIOUS;
  if (score >= 35) return RISK_LEVELS.SUSPICIOUS;
  return RISK_LEVELS.SAFE;
}

export function riskMeta(level) {
  return LEVEL_META[level] ?? LEVEL_META[RISK_LEVELS.SAFE];
}

export function formatScore(score) {
  return Math.round(score);
}