import { apiFetch } from './api';
import { mapScanDetail, mapScanSummary } from '../utils/mapScan';

export async function fetchHistory() {
  const data = await apiFetch('/history/');
  return data.map(mapScanSummary);
}

export async function fetchScanDetail(id) {
  const data = await apiFetch(`/history/${id}`);
  return mapScanDetail(data);
}