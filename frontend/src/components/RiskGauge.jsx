import { memo } from 'react'

export const RiskGauge = memo(function RiskGauge({ score }) {
  const pct = Math.round((score || 0.5) * 100)
  const color = pct >= 90 ? '#ef7f88' : pct >= 75 ? '#f4bf75' : pct >= 45 ? '#4aadff' : '#54d5a5'
  const strokeDash = `${pct * 1.26} 126`

  return (
    <div className="risk-gauge-container" role="meter" aria-valuenow={pct} aria-valuemin="0" aria-valuemax="100" aria-label="Anomaly risk score">
      <svg className="risk-gauge-svg" viewBox="0 0 50 50">
        <circle cx="25" cy="25" r="20" fill="none" stroke="#163450" strokeWidth="4" />
        <circle
          cx="25"
          cy="25"
          r="20"
          fill="none"
          stroke={color}
          strokeWidth="4"
          strokeDasharray={strokeDash}
          strokeDashoffset="0"
          transform="rotate(-90 25 25)"
          strokeLinecap="round"
        />
      </svg>
      <div className="risk-gauge-value" style={{ color }}>
        {pct}%
        <small>Anomaly Risk</small>
      </div>
    </div>
  )
})
