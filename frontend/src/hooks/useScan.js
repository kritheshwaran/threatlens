import { useCallback, useState } from 'react';
import { scanUrl } from '../services/scanService';

export const SCAN_STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
};

export function useScan() {
  const [status, setStatus] = useState(SCAN_STATUS.IDLE);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const runScan = useCallback(async (url) => {
    setStatus(SCAN_STATUS.LOADING);
    setError(null);
    try {
      const data = await scanUrl(url);
      setResult(data);
      setStatus(SCAN_STATUS.SUCCESS);
      return data;
    } catch (err) {
      setError(err.message || 'Something went wrong while scanning.');
      setStatus(SCAN_STATUS.ERROR);
      return null;
    }
  }, []);

  const reset = useCallback(() => {
    setStatus(SCAN_STATUS.IDLE);
    setResult(null);
    setError(null);
  }, []);

  return { status, result, error, runScan, reset };
}