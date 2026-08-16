import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { fetchHistory } from '../services/historyService';
import { useAuth } from './AuthContext';

const ScanHistoryContext = createContext(null);

export function ScanHistoryProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    if (!isAuthenticated) {
      setHistory([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (err) {
      setError(err.message || 'Failed to load scan history.');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const addScan = (scan) => {
    setHistory((prev) => [scan, ...prev]);
  };

  const value = useMemo(
    () => ({ history, loading, error, addScan, refresh }),
    [history, loading, error, refresh]
  );

  return (
    <ScanHistoryContext.Provider value={value}>
      {children}
    </ScanHistoryContext.Provider>
  );
}

export function useScanHistory() {
  const ctx = useContext(ScanHistoryContext);
  if (!ctx) {
    throw new Error('useScanHistory must be used within a ScanHistoryProvider');
  }
  return ctx;
}