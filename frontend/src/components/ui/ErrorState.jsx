import { AlertTriangle } from 'lucide-react';

export default function ErrorState({ title = 'Something went wrong', description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-malicious/30 bg-malicious-soft px-6 py-14 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-malicious/10 text-malicious">
        <AlertTriangle size={20} strokeWidth={1.75} />
      </span>
      <div>
        <p className="font-display text-sm font-semibold text-text-primary">{title}</p>
        {description && <p className="mt-1 max-w-sm text-sm text-text-secondary">{description}</p>}
      </div>
      {action}
    </div>
  );
}