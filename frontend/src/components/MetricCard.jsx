import { memo } from 'react'

function MetricSparkline({ tone }) {
  const strokeColor = tone === 'green' ? '#54d5a5' : tone === 'coral' ? '#ef7f88' : tone === 'violet' ? '#a79eff' : '#53aff7'
  return (
    <svg className="metric-sparkline" viewBox="0 0 100 30" preserveAspectRatio="none">
      <path
        d="M 0 22 Q 25 5, 50 18 T 100 8"
        fill="none"
        stroke={strokeColor}
        strokeWidth="2"
        opacity="0.75"
      />
    </svg>
  )
}

export const MetricCard = memo(function MetricCard({ metric }) {
  return (
    <article className={`metric-card metric-${metric.tone}`}>
      <div className="metric-icon">{metric.icon}</div>
      <p>{metric.label}</p>
      <strong>{metric.value}</strong>
      <small>{metric.change}</small>
      <MetricSparkline tone={metric.tone} />
    </article>
  )
})
