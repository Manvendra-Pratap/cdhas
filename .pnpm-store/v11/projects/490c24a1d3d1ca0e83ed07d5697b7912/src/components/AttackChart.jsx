import { memo, useMemo } from 'react'

function linePath(points, width = 760, height = 230, padding = 18) {
  if (!points || points.length === 0) return ''
  const max = Math.max(...points.map((point) => point.sessions), 1)
  return points.map((point, index) => {
    const x = padding + (index / (points.length - 1)) * (width - padding * 2)
    const y = height - padding - (point.sessions / max) * (height - padding * 2)
    return `${index === 0 ? 'M' : 'L'} ${x} ${y}`
  }).join(' ')
}

export const AttackChart = memo(function AttackChart({ timeline, compact = false }) {
  const path = useMemo(() => linePath(timeline), [timeline])
  const peak = Math.max(...(timeline ? timeline.map((point) => point.sessions) : [1]), 1)

  return (
    <section className={`card chart-card ${compact ? 'compact-chart' : ''}`}>
      <div className="card-heading">
        <div>
          <p className="eyebrow">ACTIVITY</p>
          <h2>Attack volume timeline</h2>
        </div>
        <div className="chart-key">
          <span><i className="legend-line sessions" />Sessions</span>
          <span><i className="legend-line anomalies" />Anomalies</span>
        </div>
      </div>
      <div className="chart-wrap">
        <svg viewBox="0 0 760 230" role="img" aria-label="Session activity over 24 hours" preserveAspectRatio="none">
          <defs>
            <linearGradient id="volume-fill" x1="0" x2="0" y1="0" y2="1">
              <stop stopColor="#40a7ff" stopOpacity=".26" />
              <stop offset="1" stopColor="#40a7ff" stopOpacity="0" />
            </linearGradient>
          </defs>
          {[42, 88, 134, 180].map((y) => <line key={y} x1="18" x2="742" y1={y} y2={y} className="gridline" />)}
          <path d={`${path} L 742 212 L 18 212 Z`} fill="url(#volume-fill)" />
          <path d={path} className="session-path" />
          {timeline && timeline.map((point, index) => {
            const x = 18 + (index / (timeline.length - 1)) * 724
            const y = 212 - (point.sessions / peak) * 194
            return <circle key={point.time} cx={x} cy={y} r="3.5" className="point" />
          })}
        </svg>
        <div className="axis-labels">
          {timeline && timeline.filter((_, index) => index % 2 === 0).map((point) => <span key={point.time}>{point.time}</span>)}
        </div>
      </div>
    </section>
  )
})
