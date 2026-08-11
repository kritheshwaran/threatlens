import { createContext, useContext, useMemo, useState } from 'react';
import { MOCK_SCANS } from '../data/mockData';

const ScanHistoryContext = createContext(null);

export function ScanHistoryProvider({ children }) {
  const [history, setHistory] = useState(MOCK_SCANS);

  const addScan = (scan) => {
    setHistory((prev) => [scan, ...prev]);
  };

  const value = useMemo(() => ({ history, addScan }), [history]);

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