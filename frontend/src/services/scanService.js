
// Real POST /scan implementation. Returns the same shape the mock
// implementation used to (id, url, score, level, scannedAt, factors),
// via mapScanDetail(), so useScan.js / ScanResultPanel / RiskGauge
// need no changes at all.

import { apiFetch } from './api';
import { mapScanDetail } from '../utils/mapScan';

/**
 * @param {string} url
 * @returns {Promise<{id:number,url:string,score:number,level:string,scannedAt:string,factors:Array}>}
 */
export async function scanUrl(url) {
  const data = await apiFetch('/scan/', {
    method: 'POST',
    body: JSON.stringify({ url }),
  });
  return mapScanDetail(data);
}