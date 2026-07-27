import { memo, useState, useMemo } from 'react'

const severityOrder = { Critical: 4, High: 3, Medium: 2, Low: 1 }

export const ExecutiveSummary = memo(function ExecutiveSummary({ data }) {
  const [collapsed, setCollapsed] = useState(false)

  const stats = useMemo(() => {
    const sessions = data.sessions || []
    const totalSessions = sessions.length
    const highRiskSessions = sessions.filter((s) => severityOrder[s.severity] >= 3).length
    const countries = new Set(sessions.map((s) => s.country)).size

    const archetypeCounts = {}
    sessions.forEach((s) => {
      archetypeCounts[s.archetype] = (archetypeCounts[s.archetype] || 0) + 1
    })
    const topThreat = Object.entries(archetypeCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Reconnaissance bot'

    const countryScores = {}
    sessions.forEach((s) => {
      if (!countryScores[s.country]) countryScores[s.country] = { count: 0, highRisk: 0 }
      countryScores[s.country].count += 1
      if (severityOrder[s.severity] >= 3) countryScores[s.country].highRisk += 1
    })
    const highestRiskCountry = Object.entries(countryScores).sort((a, b) => b[1].highRisk - a[1].highRisk)[0]?.[0] || 'Germany'

    const avgScore = sessions.length > 0
      ? Math.round((sessions.reduce((acc, s) => acc + (s.score || 0.5), 0) / sessions.length) * 100)
      : 64

    return {
      totalSessions,
      highRiskSessions,
      countries,
      topThreat,
      highestRiskCountry,
      avgRiskScore: `${avgScore}%`,
      lastGenerated: data.overview?.generatedAt ? new Date(data.overview.generatedAt).toLocaleTimeString() : new Date().toLocaleTimeString(),
    }
  }, [data])

  return (
    <section className="card summary-card">
      <div className="summary-header" onClick={() => setCollapsed(!collapsed)} role="button" tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && setCollapsed(!collapsed)}>
        <div>
          <p className="eyebrow">SOC EXECUTIVE SUMMARY</p>
          <h2>Security Threat Posture Overview</h2>
        </div>
        <button className="collapse-toggle" type="button" aria-expanded={!collapsed}>
          {collapsed ? 'Expand ▲' : 'Collapse ▼'}
        </button>
      </div>

      {!collapsed && (
        <div className="summary-grid">
          <div className="summary-item">
            <span>Total Sessions</span>
            <strong>{stats.totalSessions}</strong>
          </div>
          <div className="summary-item">
            <span>High Risk Sessions</span>
            <strong className="coral-text">{stats.highRiskSessions}</strong>
          </div>
          <div className="summary-item">
            <span>Countries</span>
            <strong>{stats.countries}</strong>
          </div>
          <div className="summary-item">
            <span>Top Threat</span>
            <strong className="blue-text">{stats.topThreat}</strong>
          </div>
          <div className="summary-item">
            <span>Highest Risk Country</span>
            <strong className="violet-text">{stats.highestRiskCountry}</strong>
          </div>
          <div className="summary-item">
            <span>Avg Risk Score</span>
            <strong>{stats.avgRiskScore}</strong>
          </div>
          <div className="summary-item">
            <span>Last Updated</span>
            <small>{stats.lastGenerated}</small>
          </div>
        </div>
      )}
    </section>
  )
})
