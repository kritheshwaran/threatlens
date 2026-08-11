import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

const TOOLTIP_STYLE = {
  backgroundColor: '#171F2B',
  border: '1px solid #232C3A',
  borderRadius: 8,
  fontSize: 12,
  color: '#E7ECF3',
};

export function ThreatTrendChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="safeFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#34D399" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#34D399" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="suspiciousFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#FBBF24" stopOpacity={0.3} />
            <stop offset="100%" stopColor="#FBBF24" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="maliciousFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#F87171" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#F87171" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#1A222E" vertical={false} />
        <XAxis dataKey="date" tick={{ fill: '#8D99AC', fontSize: 11 }} axisLine={{ stroke: '#232C3A' }} tickLine={false} />
        <YAxis tick={{ fill: '#8D99AC', fontSize: 11 }} axisLine={false} tickLine={false} width={32} />
        <Tooltip contentStyle={TOOLTIP_STYLE} />
        <Area type="monotone" dataKey="safe" stackId="1" stroke="#34D399" fill="url(#safeFill)" strokeWidth={1.5} />
        <Area type="monotone" dataKey="suspicious" stackId="1" stroke="#FBBF24" fill="url(#suspiciousFill)" strokeWidth={1.5} />
        <Area type="monotone" dataKey="malicious" stackId="1" stroke="#F87171" fill="url(#maliciousFill)" strokeWidth={1.5} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

const CATEGORY_COLORS = ['#4C8DFF', '#F87171', '#FBBF24', '#34D399', '#8D99AC'];

export function ThreatCategoryChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={58}
          outerRadius={90}
          paddingAngle={2}
          stroke="#111721"
          strokeWidth={2}
        >
          {data.map((entry, index) => (
            <Cell key={entry.name} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={TOOLTIP_STYLE} />
        <Legend
          verticalAlign="bottom"
          iconType="circle"
          iconSize={8}
          formatter={(value) => <span className="text-xs text-text-secondary">{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}