// This is the ONLY file that should change when the real backend
// scanning endpoint (POST /scan) is wired up. Every page/component
// calls `scanUrl()` and works with the shape returned here — swap
// the mock implementation for a `fetchScannerData('/api/scan', ...)`
// call later and nothing above this layer needs to change.

import { levelFromScore } from '../utils/risk';

const USE_MOCK = true; // flip to false once POST /scan is implemented

const MOCK_LATENCY_MS = 1400;

function randomScoreFor(url) {
  const lower = url.toLowerCase();
  if (/verify|secure|update|login|billing|account/.test(lower) && !/github|google\.com|microsoft\.com/.test(lower)) {
    return 70 + Math.floor(Math.random() * 25);
  }
  if (/^http:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(lower)) {
    return 65 + Math.floor(Math.random() * 30);
  }
  if (/bit\.ly|tinyurl|t\.co/.test(lower)) {
    return 40 + Math.floor(Math.random() * 25);
  }
  return Math.floor(Math.random() * 20);
}

function buildMockFactors(score, url) {
  const factors = [];
  if (url.startsWith('https://')) {
    factors.push({ label: 'HTTPS enabled', positive: true });
  } else {
    factors.push({ label: 'No HTTPS encryption', positive: false });
  }
  if (score > 60) {
    factors.push({ label: 'Recently registered domain', positive: false });
    factors.push({ label: 'Suspicious keywords in URL', positive: false });
  } else if (score > 30) {
    factors.push({ label: 'Domain reputation unverified', positive: false });
  } else {
    factors.push({ label: 'Established domain reputation', positive: true });
    factors.push({ label: 'No suspicious redirects', positive: true });
  }
  return factors;
}

/**
 * @param {string} url
 * @returns {Promise<{id:string,url:string,score:number,level:string,scannedAt:string,factors:Array}>}
 */
export async function scanUrl(url) {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, MOCK_LATENCY_MS));

    // Simulate an occasional failure so error states are real, not decorative.
    if (/^(bad|error|fail)/i.test(url.trim())) {
      throw new Error('Scan failed: the target did not respond in time.');
    }

    const score = randomScoreFor(url.trim());
    return {
      id: `scan_${Date.now()}`,
      url: url.trim(),
      score,
      level: levelFromScore(score),
      scannedAt: new Date().toISOString(),
      factors: buildMockFactors(score, url.trim()),
    };
  }

  // --- Real implementation (Module 2+) ---
  // const { fetchScannerData } = await import('./api');
  // return fetchScannerData('/api/scan', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ url }),
  // });
  throw new Error('Live scanning is not implemented yet.');
}