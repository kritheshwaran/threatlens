import { useState } from 'react';
import { Card, CardHeader, CardBody, Button } from '../components/ui';

function Toggle({ checked, onChange, label, description }) {
  return (
    <div className="flex items-center justify-between py-3.5">
      <div>
        <p className="text-sm font-medium text-text-primary">{label}</p>
        {description && <p className="mt-0.5 text-xs text-text-secondary">{description}</p>}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${
          checked ? 'bg-accent' : 'bg-surface2 border border-border'
        }`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
            checked ? 'translate-x-5' : 'translate-x-0.5'
          }`}
        />
      </button>
    </div>
  );
}

export default function Settings() {
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [autoScan, setAutoScan] = useState(false);
  const [strictMode, setStrictMode] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-display text-xl font-semibold text-text-primary">Settings</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Preferences shown here are session-only in Module 1 and are not persisted.
        </p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader title="Profile" subtitle="Basic account information" />
        <CardBody className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <label className="text-sm">
            <span className="mb-1.5 block text-xs font-medium text-text-secondary">Full name</span>
            <input
              type="text"
              defaultValue="Security Analyst"
              className="h-10 w-full rounded-lg border border-border bg-surface2 px-3 text-sm text-text-primary focus:border-accent focus:outline-none"
            />
          </label>
          <label className="text-sm">
            <span className="mb-1.5 block text-xs font-medium text-text-secondary">Email</span>
            <input
              type="email"
              defaultValue="analyst@threatlens.dev"
              className="h-10 w-full rounded-lg border border-border bg-surface2 px-3 text-sm text-text-primary focus:border-accent focus:outline-none"
            />
          </label>
        </CardBody>
      </Card>

      <Card className="max-w-2xl">
        <CardHeader title="Scan preferences" />
        <CardBody className="divide-y divide-border">
          <Toggle
            checked={emailAlerts}
            onChange={setEmailAlerts}
            label="Email alerts"
            description="Get notified when a scan returns a malicious verdict."
          />
          <Toggle
            checked={autoScan}
            onChange={setAutoScan}
            label="Auto-scan clipboard links"
            description="Automatically scan URLs copied to your clipboard."
          />
          <Toggle
            checked={strictMode}
            onChange={setStrictMode}
            label="Strict detection mode"
            description="Lower the threshold for flagging a URL as suspicious."
          />
        </CardBody>
      </Card>

      <div className="max-w-2xl">
        <Button onClick={handleSave}>{saved ? 'Saved' : 'Save changes'}</Button>
      </div>
    </div>
  );
}