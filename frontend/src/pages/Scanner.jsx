import { useNavigate } from 'react-router-dom';
import { ScanForm, ScanResultPanel } from '../components/scanner';
import { useScan } from '../hooks/useScan';
import { useScanHistory } from '../context/ScanHistoryContext';

export default function Scanner() {
  const { status, result, error, runScan, reset } = useScan();
  const { addScan } = useScanHistory();
  const navigate = useNavigate();

  const handleSubmit = async (url) => {
    const data = await runScan(url);
    if (data) addScan(data);
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-primary">Scanner</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Check a URL for phishing, malware, and impersonation signals.
        </p>
      </div>

      <ScanForm onSubmit={handleSubmit} loading={status === 'loading'} />
      <ScanResultPanel status={status} result={result} error={error} onReset={reset} />

      {status === 'success' && result && (
        <button
          type="button"
          onClick={() => navigate(`/report/${result.id}`)}
          className="self-start text-sm font-medium text-accent hover:text-accent-strong"
        >
          View full report →
        </button>
      )}
    </div>
  );
}