import { riskMeta, formatScore } from '../../utils/risk';

const RADIUS = 54;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const LEVEL_STROKE = {
  safe: '#34D399',
  suspicious: '#FBBF24',
  malicious: '#F87171',
};

/**
 * Circular gauge. When `scanning` is true it shows an indeterminate
 * sweep instead of a score. This is ThreatLens's one signature motion
 * moment — used only here, nowhere else in the UI.
 */
export default function RiskGauge({ score = 0, level = 'safe', scanning = false, size = 160 }) {
  const meta = riskMeta(level);
  const offset = CIRCUMFERENCE - (Math.min(Math.max(score, 0), 100) / 100) * CIRCUMFERENCE;
  const stroke = LEVEL_STROKE[level] ?? LEVEL_STROKE.safe;

  return (
    <div
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
      role="img"
      aria-label={scanning ? 'Scanning in progress' : `Risk score ${formatScore(score)} out of 100, ${meta.label}`}
    >
      <svg width={size} height={size} viewBox="0 0 120 120" className={scanning ? 'animate-sweep' : ''}>
        <circle
          cx="60"
          cy="60"
          r={RADIUS}
          fill="none"
          stroke="#232C3A"
          strokeWidth="10"
        />
        {!scanning && (
          <circle
            cx="60"
            cy="60"
            r={RADIUS}
            fill="none"
            stroke={stroke}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
            transform="rotate(-90 60 60)"
            style={{ transition: 'stroke-dashoffset 0.6s ease-out' }}
          />
        )}
        {scanning && (
          <circle
            cx="60"
            cy="60"
            r={RADIUS}
            fill="none"
            stroke="#4C8DFF"
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${CIRCUMFERENCE * 0.22} ${CIRCUMFERENCE}`}
          />
        )}
      </svg>
      <div className="absolute flex flex-col items-center">
        {scanning ? (
          <span className="font-mono text-xs text-text-secondary">Scanning…</span>
        ) : (
          <>
            <span className="font-display text-3xl font-semibold text-text-primary">
              {formatScore(score)}
            </span>
            <span className="text-[11px] uppercase tracking-wide text-text-muted">/ 100</span>
          </>
        )}
      </div>
    </div>
  );
}